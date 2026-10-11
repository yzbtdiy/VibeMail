#!/usr/bin/env python3
# Demo video recorder for vibemail: grabs frames continuously over the
# Makepad remote bridge (/g?raw=1) while driving the demo arc with the same
# tap helpers as drive-demo.py, then assembles an mp4 with ffmpeg.
#
# The bridge drops a click issued too soon after a /g grab — the grabber and
# the driver therefore share one I/O lock so a click never interleaves with
# a grab, and every state-changing tap still retries until its effect shows.
#
# Usage: python scripts/record-demo.py [port] [out.mp4]
# Start the app first (run.cmd mobile).

import json
import shutil
import subprocess
import sys
import threading
import time
import urllib.request
from pathlib import Path

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8146
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else None
BASE = f"http://127.0.0.1:{PORT}"
ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
FRAMES = BUILD / "rec_frames"
OUT = OUT or (BUILD / "demo-v0.8.0.mp4")

# Park the real cursor off-window (drive-demo.py: OS mouse events steal taps)
import ctypes
_u32 = ctypes.windll.user32
_u32.SetCursorPos(_u32.GetSystemMetrics(0) // 2, _u32.GetSystemMetrics(1) - 12)

io_lock = threading.Lock()   # /g grabs and /click must never interleave
stop_flag = threading.Event()


def get(path):
    with urllib.request.urlopen(BASE + path, timeout=15) as r:
        return r.read()


def grabber(frames, stamps):
    n = 0
    while not stop_flag.is_set():
        try:
            with io_lock:
                data = get("/g?raw=1")
            stamps.append(time.monotonic())
            (FRAMES / f"frame_{n:05d}.png").write_bytes(data)
            frames.append(n)
            n += 1
        except OSError:
            time.sleep(0.2)


def write_concat(stamps, n):
    """Concat-demuxer file with PER-FRAME durations: the grabber's rate is
    variable (a grab during an animated transition takes longer), so a
    constant -framerate presentation would warp narration sync. With real
    durations the video plays in true wall-clock time and the recorded
    segment marks map exactly."""
    lines = []
    for i in range(n):
        lines.append(f"file 'rec_frames/frame_{i:05d}.png'")
        if i + 1 < n:
            d = max(0.01, stamps[i + 1] - stamps[i])
        else:
            d = 0.1
        lines.append(f"duration {d:.3f}")
    lines.append(f"file 'rec_frames/frame_{n - 1:05d}.png'")  # concat last-frame quirk
    (BUILD / "rec_concat.txt").write_text("\n".join(lines), encoding="utf-8")


def snap():
    with io_lock:
        return json.loads(get("/snap").decode("utf-8"))["s"]


def find(text, exact=False):
    for w in snap():
        if w.get("ty") == "Splash":
            continue
        t = w.get("t", "")
        if (exact and t == text) or (not exact and text in t):
            x, y, ww, h = w["r"]
            return x + ww / 2, y + h / 2
    return None


def has(text, exact=False):
    return find(text, exact) is not None


def search_for(text, exact=False, timeout=0):
    if find(text, exact):
        return True
    t0 = time.time()
    n = 0
    while time.time() - t0 < timeout:
        dy = -2400 if n % 4 == 3 else 420
        with io_lock:
            get(f"/m?k=scroll&x=206&y=400&dy={dy}")
        time.sleep(0.7)
        if find(text, exact):
            return True
        n += 1
    return False


def tap(text, exact=False):
    hit = find(text, exact)
    tries = 0
    while (not hit or not 8 < hit[1] < 856) and tries < 10:
        dy = 420 if (not hit or hit[1] >= 792) else -2400
        with io_lock:
            get(f"/m?k=scroll&x=206&y=400&dy={dy}")
        time.sleep(0.5)
        hit = find(text, exact)
        tries += 1
    if not hit:
        raise RuntimeError(f"cannot reach '{text}'")
    # settle: boot/scroll animations move targets between find and click
    time.sleep(0.3)
    cur = find(text, exact)
    if cur:
        hit = cur
    with io_lock:
        # the bridge drops a click issued right after a /g grab: hold the
        # lock idle for a beat so the click never neighbours a grab
        time.sleep(0.45)
        get(f"/click?x={hit[0]:.0f}&y={hit[1]:.0f}&wait=1")
        get("/m?k=scroll&x=206&y=400&dy=1")
    time.sleep(1.0)


def click_expect(target, expect, exact=False, tries=5):
    for n in range(tries):
        if has(expect):            # no-scroll check: search_for(timeout>0)
            return                 # would drag the list away from the target
        pos = find(target, exact)
        print(f"  [tap] {target!r} -> {pos}")
        tap(target, exact=exact)
        if search_for(expect, timeout=4):
            return
    # failure evidence, same shape as run_routes.dump_failure
    fail_dir = BUILD / "rec_fail"
    fail_dir.mkdir(parents=True, exist_ok=True)
    try:
        (fail_dir / "fail.png").write_bytes(get("/g?raw=1"))
        (fail_dir / "snap.json").write_bytes(json.dumps(snap()).encode("utf-8"))
    except OSError:
        pass
    raise RuntimeError(f"click '{target}' never produced '{expect}' (evidence: {fail_dir})")


def hold(seconds):
    time.sleep(seconds)


# ---- title / end cards ------------------------------------------------------

def make_card(path, lines):
    """Pillow's _imaging is broken on this Python — render the card with
    ffmpeg's drawtext instead (one textfile per line avoids CJK/quote
    escaping through the filter parser)."""
    color = "0xeaeae3"
    total_h = sum(size * 1.6 for _, size, _ in lines)
    y = (1720 - total_h) / 2
    parts = []
    for i, (text, size, rgb) in enumerate(lines):
        tf = BUILD / f"rec_card_{i}.txt"
        tf.write_text(text, encoding="utf-8")
        # ffmpeg filter parser: escape the drive-letter colon in paths
        tf_esc = tf.as_posix().replace(":/", "\\:/")
        hexcol = "0x%02x%02x%02x" % rgb
        parts.append(
            f"drawtext=textfile='{tf_esc}':fontfile='C\\:/Windows/Fonts/msyh.ttc'"
            f":fontsize={size}:fontcolor={hexcol}"
            f":x=(w-text_w)/2:y={y:.0f}")
        y += size * 1.6
    r = subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c={color}:s=824x1720:d=1",
         "-vf", ",".join(parts), "-frames:v", "1", str(path)],
        capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-1200:])
        raise SystemExit("ffmpeg card render failed")


# ---- the demo arc -----------------------------------------------------------

marks = []          # (segment key, seconds since capture start)
_t_start = [0.0]


def mark(key):
    marks.append((key, time.monotonic() - _t_start[0]))


def arc():
    mark("inbox")
    hold(5.0)                                   # inbox: greeting + mood line
    mark("filter")
    click_expect("专注", "已按 vibe 筛选", exact=True)
    hold(3.0)
    click_expect("全部", "周末去海边", exact=True)
    hold(1.5)
    mark("detail")
    click_expect("周末去海边", "AI 三行摘要")     # detail: summary + schedule card
    hold(4.0)
    mark("schedule")
    search_for("点按 ±1h", timeout=4)
    hold(1.0)
    click_expect("±1h", "已 +1h")               # schedule: user can adjust
    hold(2.0)
    mark("compose")
    click_expect("回复", "语气滑杆", exact=True)  # compose
    hold(2.0)
    mark("tone")
    tap("幽默", exact=True)
    hold(1.6)
    tap("专业", exact=True)
    hold(1.6)
    click_expect("正式", "正式得体", exact=True)
    hold(2.0)
    mark("draft")
    click_expect("存为草稿", "已存草稿")          # draft loop (练习标注)
    hold(2.5)
    click_expect("收件箱", "未读邮件", exact=True)
    hold(1.2)
    mark("orbit")
    click_expect("星轨", "气泡大小", exact=True)  # drift star map
    hold(4.0)
    mark("timeline")
    click_expect("时间轴", "按时间从新到旧", exact=True)
    hold(3.5)
    mark("weekly")
    click_expect("周报", "本周邮件天气", exact=True)
    hold(3.5)
    mark("dark")
    click_expect("我的", "外观主题", exact=True)
    tap("暗色", exact=True)                      # dark theme (visual flip)
    hold(2.5)
    click_expect("星轨", "漂移", exact=True)     # orbit remembers the segment:
    click_expect("漂移", "气泡大小", exact=True)  # land (any mode), then drift
    hold(2.5)
    mark("outro")
    click_expect("我的", "外观主题", exact=True)
    tap("亮色", exact=True)                      # back to light for the outro
    hold(1.2)
    click_expect("收件箱", "未读邮件", exact=True)
    hold(2.5)
    mark("end")


def main():
    assemble_only = "--assemble" in sys.argv
    if assemble_only and FRAMES.exists():
        meta = json.loads((BUILD / "rec_marks.json").read_text(encoding="utf-8"))
        stamps = json.loads((BUILD / "rec_stamps.json").read_text(encoding="utf-8"))
        n = len(stamps)
        write_concat(stamps, n)
        print(f"[assemble] reusing {n} captured frames, per-frame timing")
    else:
        if FRAMES.exists():
            shutil.rmtree(FRAMES)
        FRAMES.mkdir(parents=True)
        t0 = time.time()
        while not (has("未读邮件") or has("未添加邮箱账号")):
            if time.time() - t0 > 25:
                raise SystemExit("app never reached the inbox")
            time.sleep(0.5)
        print("[rec] boot seen, starting capture")

        frames, stamps = [], []
        th = threading.Thread(target=grabber, args=(frames, stamps), daemon=True)
        th.start()
        t_start = time.monotonic()
        _t_start[0] = t_start
        arc()
        stop_flag.set()
        th.join(timeout=5)
        span = time.monotonic() - t_start
        n = len(frames)
        stamps = [s - t_start for s in stamps]          # video-relative seconds
        (BUILD / "rec_stamps.json").write_text(json.dumps(stamps), encoding="utf-8")
        (BUILD / "rec_marks.json").write_text(
            json.dumps({"fps": n / span if span > 0 else 6.0, "span": span,
                        "marks": marks}, ensure_ascii=False, indent=1),
            encoding="utf-8")
        write_concat(stamps, n)
        print(f"[rec] captured {n} frames over {span:.1f}s, per-frame timing")
        print(f"[rec] {len(marks)} segment marks -> build/rec_marks.json")

    title = BUILD / "rec_title.png"
    end = BUILD / "rec_end.png"
    make_card(title, [("VibeMail", 96, (26, 25, 23)),
                      ("有情绪的邮件", 44, (90, 88, 82)),
                      ("OctoSense · Agent2App 2026", 26, (140, 136, 126))])
    make_card(end, [("VibeMail", 72, (26, 25, 23)),
                    ("github.com/yzbtdiy/VibeMail", 28, (90, 88, 82))])

    OUT.parent.mkdir(parents=True, exist_ok=True)
    filt = ("[0:v]scale=824:1720,fps=30[v0];"
            f"[1:v]scale=824:1720,fps=30[v1];"
            "[2:v]scale=824:1720,fps=30[v2];"
            "[v0][v1][v2]concat=n=3:v=1[v]")
    cmd = ["ffmpeg", "-y",
           "-loop", "1", "-t", "3", "-i", str(title),
           "-f", "concat", "-safe", "0", "-i", str(BUILD / "rec_concat.txt"),
           "-loop", "1", "-t", "2.5", "-i", str(end),
           "-filter_complex", filt, "-map", "[v]",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", str(OUT)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2000:])
        raise SystemExit("ffmpeg failed")
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration,size",
         "-of", "default=nw=1", str(OUT)], capture_output=True, text=True)
    print(f"[done] {OUT}\n{probe.stdout.strip()}")


if __name__ == "__main__":
    main()
