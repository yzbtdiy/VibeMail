#!/usr/bin/env python3
# Narration + subtitle pass for the recorded demo: reads the segment marks
# record-demo.py captured (build/rec_marks.json), voices each segment's line
# with edge-tts (zh-CN-XiaoxiaoNeural), mixes the clips at their segment
# times and burns matching subtitles with drawtext.
#
# Usage: python scripts/narrate-demo.py [demo.mp4] [out.mp4]
# Re-runnable: audio is regenerated per line, the video is re-muxed.

import asyncio
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
NARR = BUILD / "narr"
DEMO = Path(sys.argv[1]) if len(sys.argv) > 1 else BUILD / "demo-v0.8.0.mp4"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else BUILD / "demo-v0.8.0-narr.mp4"
TITLE_LEN = 3.0          # the title card prepended by record-demo.py
VOICE = "zh-CN-XiaoxiaoNeural"
RATE = "+10%"

LINES = {
    "title":    "VibeMail,有情绪的邮件。",
    "inbox":    "收件箱按五种情绪分类,心情播报一眼看清今天。",
    "filter":   "点按情绪芯片,只看当下想处理的邮件。",
    "detail":   "打开邮件,先看 AI 三行摘要。",
    "schedule": "识别到安排:日程自动提取,可微调,可导出。",
    "compose":  "写回信,拖动语气滑杆。",
    "tone":     "同一句话,在真诚随意与正式得体之间实时改写。",
    "draft":    "没想好,就先存为草稿。",
    "orbit":    "星轨:气泡大小是重要度,颜色是情绪。",
    "timeline": "时间轴,按时间梳理每一封邮件。",
    "weekly":   "周报是本地统计,不出你的设备。",
    "dark":     "暖纸与炭黑,两种主题随时切换。",
    "outro":    "VibeMail,让邮件有情绪。",
}


def ffprobe_duration(path):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True)
    return float(r.stdout.strip())


async def gen_audio(key, text, path):
    import edge_tts
    await edge_tts.Communicate(text, VOICE, rate=RATE).save(str(path))


def main():
    meta = json.loads((BUILD / "rec_marks.json").read_text(encoding="utf-8"))
    marks = [("title", -TITLE_LEN)] + [(k, t) for k, t in meta["marks"]]
    marks.append(("endcard", meta["span"]))
    total = TITLE_LEN + meta["span"] + 2.5

    # segment windows in video time (title card is TITLE_LEN long)
    segs = []
    for i, (key, t) in enumerate(marks[:-1]):
        if key == "end":
            continue
        start = t + TITLE_LEN
        end = marks[i + 1][1] + TITLE_LEN
        segs.append((key, max(0.0, start), end))

    NARR.mkdir(parents=True, exist_ok=True)
    clips = []
    for key, start, end in segs:
        text = LINES.get(key)
        if not text:
            continue
        mp3 = NARR / f"{key}.mp3"
        asyncio.run(gen_audio(key, text, mp3))
        dur = ffprobe_duration(mp3)
        clips.append((key, text, start, end, dur))
        flag = " <-- LONGER THAN SEGMENT" if dur > end - start else ""
        print(f"  [{key:8s}] {start:6.2f}s dur {dur:4.2f}s (window {end - start:4.2f}s){flag}")

    # audio: each clip delayed to just AFTER its segment's visual lands —
    # the mark is recorded when the tap BEGINS and the transition takes
    # ~2.8s, so narration follows the picture instead of leading it
    OFFSETS = {"title": 0.5, "inbox": 0.8}
    def seg_offset(key):
        return OFFSETS.get(key, 2.6)
    ins = ["-i", str(DEMO)]
    for i, (key, *_rest) in enumerate(clips):
        ins += ["-i", str(NARR / f"{key}.mp3")]
    aparts = []
    labels = []
    for i, (key, _t, start, _e, _d) in enumerate(clips):
        ms = int((start + seg_offset(key)) * 1000)
        aparts.append(f"[{i + 1}:a]adelay={ms}|{ms}[a{i}]")
        labels.append(f"[a{i}]")
    amix = ";".join(aparts) + ";" + "".join(labels) + \
        f"amix=inputs={len(clips)}:normalize=0[aout]"

    # subtitles: one drawtext per segment, enabled inside its window
    vparts = []
    for i, (key, text, start, end, dur) in enumerate(clips):
        tf = NARR / f"sub_{key}.txt"
        tf.write_text(text, encoding="utf-8")
        tf_esc = tf.as_posix().replace(":/", "\\:/")
        sub_start = start + max(0.4, seg_offset(key) - 0.2)
        sub_end = min(sub_start + dur + 0.8, end - 0.05)
        vparts.append(
            f"drawtext=textfile='{tf_esc}':fontfile='C\\:/Windows/Fonts/msyh.ttc'"
            f":fontsize=32:fontcolor=white:borderw=0"
            f":box=1:boxcolor=black@0.45:boxborderw=12"
            f":x=(w-text_w)/2:y=1450"
            f":enable='between(t,{sub_start:.2f},{sub_end:.2f})'")
    vchain = ",".join(vparts) + "[vout]"

    cmd = ["ffmpeg", "-y", *ins,
           "-filter_complex", amix + ";" + vchain,
           "-map", "[vout]", "-map", "[aout]",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
           "-c:a", "aac", "-b:a", "128k", "-t", f"{total:.2f}", str(OUT)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2400:])
        raise SystemExit("ffmpeg narrate failed")
    print(f"[done] {OUT}  ({ffprobe_duration(OUT):.1f}s, "
          f"{OUT.stat().st_size / 1048576:.1f} MB)")


if __name__ == "__main__":
    main()
