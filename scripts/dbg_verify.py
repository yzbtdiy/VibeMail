#!/usr/bin/env python3
"""Verify specific texts survive on a live 412 instance: the GitHub row in
the inbox and the autonomy-scale row at the bottom of the agents screen."""
import ctypes, json, sys, time, urllib.request

PORT = sys.argv[1] if len(sys.argv) > 1 else "8146"
BASE = f"http://127.0.0.1:{PORT}"

def get(p):
    return urllib.request.urlopen(BASE + p, timeout=15).read()

def snap():
    return json.loads(get("/snap").decode("utf-8"))["s"]

def texts():
    return {w.get("t", "") for w in snap() if w.get("t") and w.get("ty") != "Splash"}

def find_in(t, needle):
    return any(needle in x for x in t)

def tap(text):
    for _ in range(10):
        for w in snap():
            if w.get("ty") != "Splash" and w.get("t") and text in w["t"]:
                x, y, ww, h = w["r"]
                cx, cy = x + ww / 2, y + h / 2
                if 29 < cy < 766 or 776 < cy < 855:
                    get(f"/click?x={cx:.0f}&y={cy:.0f}&wait=1")
                    time.sleep(1.4)
                    return True
        get("/m?k=scroll&x=200&y=400&dy=420")
        time.sleep(0.5)
    return False

ctypes.windll.user32.SetCursorPos(3800, 200)

# inbox: scroll slowly to the GitHub row
seen = set()
for _ in range(12):
    seen |= texts()
    get("/m?k=scroll&x=200&y=400&dy=300")
    time.sleep(0.8)
seen |= texts()
print("inbox GitHub subject:", find_in(seen, "调度器重构"))
print("inbox priority 94:", find_in(seen, "94"), "| 61:", find_in(seen, "61"), "| 88:", find_in(seen, "88"))

# agents: scroll slowly to the bottom
for _ in range(3):
    get("/m?k=scroll&x=200&y=400&dy=-6000"); time.sleep(0.3)
if tap("Agent"):
    time.sleep(1.2)
    seen = set()
    for _ in range(14):
        seen |= texts()
        get("/m?k=scroll&x=200&y=400&dy=300")
        time.sleep(0.8)
    seen |= texts()
    print("agents 全自动:", find_in(seen, "全自动"))
    print("agents 仅建议:", find_in(seen, "仅建议"))
    print("agents SEMI-AUTO:", find_in(seen, "SEMI-AUTO"))
    print("agents LIVE:", find_in(seen, "● LIVE"))
