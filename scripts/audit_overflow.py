#!/usr/bin/env python3
"""Right-edge overflow audit: launch card-host at several widths, walk every
screen, and report any widget whose rect crosses the window's right edge.

usage: python scripts/audit_overflow.py [width ...]   (default 412 700 1200)
"""
import ctypes
import json
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

def find(text):
    for w in snap():
        if w.get("ty") == "Splash":
            continue
        if w.get("t") and text in w["t"]:
            x, y, ww, h = w["r"]
            return (x + ww / 2, y + h / 2)
    return None

def tap(text):
    for _ in range(10):
        p = find(text)
        if p and (29 < p[1] < 766 or 776 < p[1] < 855):
            get(f"/click?x={p[0]:.0f}&y={p[1]:.0f}&wait=1")
            time.sleep(1.3)
            return True
        get("/m?k=scroll&x=200&y=400&dy=" + ("420" if (not p or p[1] >= 766) else "-2400"))
        time.sleep(0.5)
    return False

def to_top():
    for _ in range(3):
        get("/m?k=scroll&x=200&y=400&dy=-6000")
        time.sleep(0.3)

def overflow(win_w):
    """Widgets whose right edge passes the window edge (2px slack)."""
    out = []
    for w in snap():
        r = w.get("r")
        if not r or w.get("ty") in ("Window", "KeyboardView", "Splash"):
            continue
        if r[0] + r[2] > win_w + 2:
            t = (w.get("t") or "")[:26]
            out.append((w.get("ty"), r, t))
    return out

def audit_width(width):
    subprocess.run(["taskkill", "/im", "card-host.exe", "/f"],
                   capture_output=True)
    time.sleep(1.5)
    env = dict(__import__("os").environ, MAKEPAD_REMOTE=PORT)
    proc = subprocess.Popen(
        [CARD_HOST, "--bundle", "bundle", "--app-data", ".local-state-audit",
         "--allow-unsigned", "--stamp", "--size", f"{width}x860"],
        cwd=APP, env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t0 = time.time()
    while time.time() - t0 < 20:
        try:
            get("/log?n=1")
            if find("已分诊今日") or find("未添加邮箱账号"):
                break
        except OSError:
            pass
        time.sleep(0.6)

    ctypes.windll.user32.SetCursorPos(ctypes.windll.user32.GetSystemMetrics(0)//2, ctypes.windll.user32.GetSystemMetrics(1)-12)
    issues = []
    # inbox
    to_top(); time.sleep(0.5)
    issues += [("inbox", *i) for i in overflow(width)]
    # scroll the inbox to the bottom too
    for _ in range(4):
        get("/m?k=scroll&x=200&y=400&dy=500"); time.sleep(0.4)
    issues += [("inbox-scrolled", *i) for i in overflow(width)]
    # read view
    to_top()
    if tap("Re: Q4 联名方案"):
        time.sleep(1.0)
        issues += [("read-top", *i) for i in overflow(width)]
        for _ in range(4):
            get("/m?k=scroll&x=200&y=400&dy=500"); time.sleep(0.4)
        issues += [("read-scrolled", *i) for i in overflow(width)]
    # write view
    to_top()
    if tap("写信"):
        time.sleep(1.0)
        issues += [("write-top", *i) for i in overflow(width)]
        for _ in range(3):
            get("/m?k=scroll&x=200&y=400&dy=500"); time.sleep(0.4)
        issues += [("write-scrolled", *i) for i in overflow(width)]
    # agents view
    to_top()
    if tap("Agent"):
        time.sleep(1.0)
        issues += [("agents-top", *i) for i in overflow(width)]
        for _ in range(4):
            get("/m?k=scroll&x=200&y=400&dy=500"); time.sleep(0.4)
        issues += [("agents-scrolled", *i) for i in overflow(width)]

    proc.kill()
    return issues

def main():
    widths = [int(a) for a in sys.argv[1:]] or [412, 700, 1200]
    all_issues = {}
    for w in widths:
        print(f"=== {w}px ===", flush=True)
        iss = audit_width(w)
        all_issues[w] = iss
        if not iss:
            print("  clean")
        for screen, ty, r, t in iss:
            print(f"  [{screen}] {ty} r={r} right={r[0]+r[2]} t={t!r}")
    Path(APP / "build" / "overflow-report.txt").write_text(
        "\n".join(f"{w}: {i}" for w, lst in all_issues.items() for i in lst),
        encoding="utf-8")

if __name__ == "__main__":
    main()
