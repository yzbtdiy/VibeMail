#!/usr/bin/env python3
"""Missing-content audit: for each width, boot a FRESH instance per screen
and diff the texts that SHOULD be visible against what /snap reports while
sweeping the single scroll column. In this stack a squeezed widget vanishes
from the tree entirely (its rect never overflows), so right-edge audits
cannot see it — presence checks can.

One fresh boot per (width, screen): a long-lived instance that harvests,
taps, harvests again fights several bridge/runtime quirks at once (clicks
riding scroll drift, screens flipping back after async host replies — both
probed); every probe of the boot-tap-harvest pattern is stable.

usage: python scripts/audit_missing.py [width ...]   (default 412 700 1200)
"""
import ctypes
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

APP = Path(__file__).resolve().parent.parent
CARD_HOST = r"D:\Users\yzbtdiy\Cache\CARGO_TARGET\release\card-host.exe"
PORT = "8145"
BASE = f"http://127.0.0.1:{PORT}"


def get(p):
    return urllib.request.urlopen(BASE + p, timeout=15).read()


def snap():
    return json.loads(get("/snap").decode("utf-8"))["s"]


def visible_texts():
    """Everything currently in the (visible) tree."""
    return {w.get("t", "") for w in snap() if w.get("t") and w.get("ty") != "Splash"}


def find(text, exact=False):
    for w in snap():
        if w.get("ty") == "Splash":
            continue
        t = w.get("t", "")
        if (exact and t == text) or (not exact and t and text in t):
            x, y, ww, h = w["r"]
            return (x + ww / 2, y + h / 2)
    return None


def wait_scroll_stable(timeout=6.0):
    """Wheel injection arms inertia and rubber-band bounce; sample a
    viewport landmark until three reads 0.3s apart agree."""
    def landmark():
        ys = sorted(w["r"][1] for w in snap()
                    if w.get("r") and w.get("ty") not in (None, "Window", "KeyboardView", "Splash"))
        return tuple(ys[:12]) or None
    t0 = time.time()
    streak = 0
    last = None
    while time.time() - t0 < timeout:
        cur = landmark()
        if last is not None and cur == last:
            streak += 1
            if streak >= 3:
                return
        else:
            streak = 0
        last = cur
        time.sleep(0.3)


def boot(width, pre_tap=None, expect=None, exact=False, tries=4):
    """Fresh card-host at width; optionally one stable tap (pre_tap) whose
    effect is verified by `expect`. Returns (proc, harvested_texts_fn)."""
    subprocess.run(["taskkill", "/im", "card-host.exe", "/f"], capture_output=True)
    time.sleep(1.2)
    env = dict(os.environ, MAKEPAD_REMOTE=PORT)
    bundle = "build/run-bundle" if (APP / "build/run-bundle/manifest.json").exists() else "bundle"
    proc = subprocess.Popen(
        [CARD_HOST, "--bundle", bundle,
         "--app-data", ".local-state-audit",
         "--allow-unsigned", "--stamp", "--size", f"{width}x860"],
        cwd=APP, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t0 = time.time()
    while time.time() - t0 < 20:
        try:
            get("/log?n=1")
            if find("未读邮件") or find("未添加邮箱账号"):
                break
        except OSError:
            pass
        time.sleep(0.6)
    ctypes.windll.user32.SetCursorPos(
        ctypes.windll.user32.GetSystemMetrics(0) // 2,
        ctypes.windll.user32.GetSystemMetrics(1) - 12)
    time.sleep(1.5)          # let the boot repaint + mail reply land

    if pre_tap:
        for n in range(tries):
            if expect and find(expect):
                break
            pos = find(pre_tap, exact)
            if pos:
                get(f"/click?x={pos[0]:.0f}&y={pos[1]:.0f}&wait=1")
                time.sleep(1.4)
        if expect and not find(expect):
            proc.kill()
            raise RuntimeError(f"tap {pre_tap!r} never produced {expect!r}")
    return proc


def harvest(sx):
    """Sweep the single scroll column top-to-bottom in SMALL steps (a big
    dy flings past a short screen and the middle texts are never sampled),
    collecting every visible text."""
    seen = set()
    for _ in range(3):
        get(f"/m?k=scroll&x={sx}&y=400&dy=-6000")
        time.sleep(0.25)
    wait_scroll_stable()
    for _ in range(26):
        seen |= visible_texts()
        get(f"/m?k=scroll&x={sx}&y=400&dy=300")
        time.sleep(0.35)
    seen |= visible_texts()
    wait_scroll_stable()
    return seen


EXPECTED = {
    "inbox": [
        "未读邮件", "今天有", "未添加邮箱账号",
        "全部", "专注", "愉悦", "平静", "灵感", "连接",
        # every card: sender + subject + snippet head + vibe chip + score
        "Mira", "周末去海边", "就是上次你说想住的那家",
        "云服务账单", "10 月账单已生成", "本期用量超出套餐",
        "产品周报 · Aurora", "第 42 期", "这周我们学会的第一件事",
        "GitHub", "你关注的仓库本周有 14 个更新", "新增 headless 测试章节",
        "读书会 · 山雾小组", "十一月共读书目投票", "目前《夜晚的潜水艇》7 票",
        "外婆", "院子里的桂花开了", "今年开得早",
        "设计系统双周报", "Vol.19 高斯模糊", "从 aurora 渐变到毛玻璃",
        "HR · OctoSense", "黑客松作品提交确认", "请在周三前确认",
        "重要度 92", "重要度 86", "重要度 95",
        "收件箱", "星轨", "写信", "我的",
    ],
    "detail-mira": [
        "收件箱",  # the back row
        "愉悦",
        "周末去海边吗?我订到那间玻璃小屋了!",
        "Mira · mira@octomail.io · 08:47",
        "AI 三行摘要", "练习摘要",
        "Mira 订到了心仪的海边玻璃小屋",
        "周六早出发、周日傍晚返回",
        "需要你回复选择哪一班火车",
        "就是上次你说想住的那家,推开窗就是海。",
        "星标", "归档", "回复",
    ],
    "orbit": [
        "星轨", "气泡大小 = 重要度 · 颜色 = vibe · 点按打开",
        # 0.7.1: bubbles show the short display name (bname), like the
        # reference's sender.slice(0, 6)
        "Mira", "云服务账单", "产品周报", "GitHub",
        "读书会", "外婆", "设计双周报", "HR",
    ],
    "write": [
        "写信", "收件人", "mira@octomail.io", "主题", "Re: 周末去海边吗?",
        "语气滑杆 · AI 实时改写", "真诚", "友好", "正式", "回信预览",
        "发送",
    ],
    "set": [
        "设置", "外观主题", "暖纸亮色 / 炭黑暗色",
        "跟随系统", "亮色", "暗色", "当前:",
        "OctoSense 能力声明", "最小权限 · 密码由平台保管",
        "mail", "storage", "model", "刻意不声明",
        # card-host: the reference mail service answers with no account ->
        # 添加账号; the 重试连接 button only exists in the error states
        "邮箱账号", "添加账号",
        "练习:模拟发送失败", "账号", "me@octomail.io",
        "VibeMail 0.7.2",
    ],
}

# screen -> (pre_tap, expect): one stable tap after boot, verified.
# Nav labels MUST be exact: e.g. the inbox digest line "…在「我的」里添加"
# substring-matches 我的 and swallows the click (probed).
SCREENS = [
    ("inbox", None, None),
    ("detail-mira", "周末去海边", "mira@octomail.io"),
    ("orbit", "星轨", "气泡大小", True),
    ("write", "写信", "语气滑杆", True),
    ("set", "我的", "外观主题", True),
]


def audit_width(width):
    sx = width // 2          # the phone column is centred
    missing = {}
    for row in SCREENS:
        name, pre_tap, expect = row[0], row[1], row[2]
        exact = row[3] if len(row) > 3 else False
        try:
            proc = boot(width, pre_tap, expect, exact)
        except RuntimeError as e:
            missing[name] = [f"BOOT/TAP FAILED: {e}"]
            continue
        seen = harvest(sx)
        proc.kill()
        absent = [e for e in EXPECTED[name] if not any(e in t for t in seen)]
        missing[name] = absent
        print(f"  [{name}] {'complete' if not absent else 'MISSING ' + str(len(absent))}",
              flush=True)
        for a in absent:
            print(f"    - {a!r}")
    return missing


def main():
    widths = [int(a) for a in sys.argv[1:]] or [412, 700, 1200]
    report = []
    for w in widths:
        print(f"=== {w}px ===", flush=True)
        miss = audit_width(w)
        for screen, absent in miss.items():
            for a in absent:
                report.append(f"{w} {screen}: {a}")
    Path(APP / "build" / "missing-report.txt").write_text(
        "\n".join(report), encoding="utf-8")
    if report:
        print(f"{len(report)} missing entries -> build/missing-report.txt")
        sys.exit(1)
    print("all screens complete at every width; report -> build/missing-report.txt")


if __name__ == "__main__":
    main()
