#!/usr/bin/env python3
# Demo driver for vibemail 0.7.0: drives the real card-host window over the
# Makepad remote bridge (GET /snap, /click, /t, /m, /g) and captures the
# listing screenshots plus the reply-lifecycle evidence shots.
#
# Phone-column UI (0.7.0): a 412 logical px column (status bar, screen
# bodies that each scroll, docked glass nav pill), five vibes with aura
# halos, the orbit star map with drifting bubbles, the tone-slider compose
# and the settings screen. Boots in the warm-paper light theme; the 我的
# screen flips to charcoal dark.
#
# Bridge quirks this driver works around, observed on the Windows build:
#   - a click issued too soon after a /g grab can be dropped -> every
#     state-changing click retries until the expected text appears;
#   - /snap reports only VISIBLE widgets -> taps scroll targets back into
#     range, expects hunt up/down for text landed outside the viewport;
#   - the drawn frame lags the widget tree by one redraw        -> shots
#     nudge a 1px scroll and wait for two identical grabs.
#
# Usage: python scripts/drive-demo.py [port]

import ctypes
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8146

# Park the REAL mouse cursor at the taskbar centre, away from the driven
# window: OS mouse events at the real cursor interleave with the bridge's
# synthetic ones — they steal taps — and a corner cursor drags the resize
# grip and shrinks the window mid-run.
_user32 = ctypes.windll.user32
_sw, _sh = _user32.GetSystemMetrics(0), _user32.GetSystemMetrics(1)
_user32.SetCursorPos(_sw // 2, _sh - 12)

BASE = f"http://127.0.0.1:{PORT}"
ROOT = Path(__file__).resolve().parent.parent
EVID = ROOT / "evidence"
SHOTS = ROOT / "bundle" / "screenshots"
EVID.mkdir(parents=True, exist_ok=True)


def get(path):
    with urllib.request.urlopen(BASE + path, timeout=15) as r:
        return r.read()


def snap():
    return json.loads(get("/snap").decode("utf-8"))["s"]


def find(text, exact=False):
    for w in snap():
        # ty "Splash" carries the WHOLE PROGRAM SOURCE as its text — it
        # substring-matches every string in the app; never a click target.
        if w.get("ty") == "Splash":
            continue
        t = w.get("t", "")
        if (exact and t == text) or (not exact and text in t):
            x, y, ww, h = w["r"]
            return x + ww / 2, y + h / 2
    return None


def has(text):
    return find(text) is not None


def wait_for(text, timeout=8):
    t0 = time.time()
    while time.time() - t0 < timeout:
        if has(text):
            return
        time.sleep(0.5)
    raise RuntimeError(f"never saw '{text}'")


def settled_pos(text, exact=False, timeout=6.0):
    t0 = time.time()
    last = find(text, exact)
    while time.time() - t0 < timeout:
        time.sleep(0.3)
        cur = find(text, exact)
        if last and cur and abs(cur[1] - last[1]) < 6 and abs(cur[0] - last[0]) < 6:
            return cur
        last = cur
    return last


def to_top():
    for _ in range(3):
        get("/m?k=scroll&x=206&y=400&dy=-6000")
        time.sleep(0.3)


def tap(text, exact=False):
    hit = find(text, exact)
    tries = 0
    def in_range(p):
        # no status bar: the detail back row starts at y~12
        return p and 8 < p[1] < 856
    while (not in_range(hit)) and tries < 10:
        dy = 420 if (not hit or hit[1] >= 792) else -2400
        get(f"/m?k=scroll&x=206&y=400&dy={dy}")
        time.sleep(0.5)
        hit = find(text, exact)
        tries += 1
    if not in_range(hit):
        raise RuntimeError(f"cannot reach widget '{text}'")
    hit = settled_pos(text, exact)
    cx, cy = hit
    get(f"/click?x={cx:.0f}&y={cy:.0f}&wait=1")
    get("/m?k=scroll&x=206&y=400&dy=1")      # flush one redraw
    time.sleep(1.2)


def search_for(text, exact=False, timeout=0):
    if find(text, exact):
        return True
    t0 = time.time()
    n = 0
    while time.time() - t0 < timeout:
        dy = -2400 if n % 2 == 0 else 620
        get(f"/m?k=scroll&x=206&y=400&dy={dy}")
        time.sleep(0.7)
        if find(text, exact):
            return True
        n += 1
    return False


def click_expect(target, expect, tries=4, exact=False):
    for n in range(tries):
        if search_for(expect):
            return
        print(f"  [try {n}] target={target!r} expect_seen={has(expect)}")
        tap(target, exact=exact)
        if search_for(expect, timeout=5):
            return
    if not search_for(expect):
        raise RuntimeError(f"click '{target}' never produced '{expect}'")


def grab(name, directory=SHOTS, settle=True):
    """Grab the window; nudge a 1px scroll first so the grabber emits a
    fresh frame (the drawn frame lags the widget tree by one redraw)."""
    if settle:
        get("/m?k=scroll&x=206&y=400&dy=1")
        time.sleep(0.45)
        data = get("/g?raw=1")
        time.sleep(0.2)
    data = get("/g?raw=1")
    out = Path(directory) / f"{name}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    print(f"  shot {out.relative_to(ROOT)} ({len(data)} b)")


if __name__ == "__main__":
    print("== vibemail demo run ==")
    wait_for("未读邮件", timeout=25)

    # -- listing 01: inbox (light)
    to_top()
    time.sleep(0.5)
    grab("01-inbox")
    grab("ev-01-boot-inbox", EVID)

    # -- evidence: vibe filter is real
    click_expect("专注", "已按 vibe 筛选:专注", exact=True)
    grab("ev-02-filter-focus", EVID)
    click_expect("全部", "周末去海边", exact=True)

    # -- listing 04 + evidence: detail with AI 三行摘要
    click_expect("周末去海边", "mira@octomail.io")
    grab("04-detail")
    grab("ev-03-detail-summary", EVID)

    # -- evidence: tone slider rewrites the preview (Mira thread)
    click_expect("回复", "语气滑杆", exact=True)
    click_expect("真诚", "玻璃小屋也太棒了吧", exact=True)
    grab("ev-04-tone-casual", EVID)
    click_expect("正式", "Mira 你好,感谢安排", exact=True)
    grab("ev-05-tone-formal", EVID)

    # -- listing 03: compose with the tone slider
    click_expect("友好", "自然友好", exact=True)
    grab("03-compose")

    # -- evidence: single-tap send happy path
    click_expect("发送", "已随波寄出", exact=True)
    grab("ev-06-sent", EVID)
    click_expect("收件箱", "未读邮件", exact=True)
    if not search_for("已回复"):
        raise RuntimeError("inbox did not show the 已回复 chip")
    grab("ev-07-replied-chip", EVID)

    # -- listing 02: orbit star map
    click_expect("星轨", "气泡大小", exact=True)
    time.sleep(1.0)
    grab("02-orbit")

    # -- evidence: outage -> failed -> switch off -> resend succeeds
    click_expect("我的", "外观主题", exact=True)
    click_expect("已关闭", "已开启", exact=True)
    click_expect("收件箱", "未读邮件", exact=True)
    click_expect("院子里的桂花开了", "grandma@family.mail")
    click_expect("回复", "语气滑杆", exact=True)
    click_expect("发送", "发送失败 · 点按重试", exact=True)
    grab("ev-08-send-failed", EVID)
    click_expect("我的", "外观主题", exact=True)
    click_expect("已开启", "已关闭", exact=True)
    click_expect("收件箱", "未读邮件", exact=True)
    click_expect("院子里的桂花开了", "grandma@family.mail")
    click_expect("回复", "语气滑杆", exact=True)
    click_expect("发送", "已随波寄出", exact=True)
    grab("ev-09-retry-sent", EVID)

    # -- listing 05 + evidence: charcoal dark theme
    click_expect("我的", "外观主题", exact=True)
    click_expect("暗色", "当前:炭黑暗色", exact=True)
    grab("ev-10-dark-set", EVID)
    click_expect("收件箱", "未读邮件", exact=True)
    grab("05-dark")
    # leave the app in the light theme (回到设置切亮色,再回收件箱)
    click_expect("我的", "外观主题", exact=True)
    click_expect("亮色", "当前:暖纸亮色", exact=True)
    click_expect("收件箱", "未读邮件", exact=True)

    print("done — listing screenshots + ev-01..10 captured")
