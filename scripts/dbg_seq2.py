#!/usr/bin/env python3
"""Replicate the demo's exact first steps, printing selection state after
each, to find what reverts the in-place reader."""
import ctypes, json, time, urllib.request

u = ctypes.windll.user32
u.SetCursorPos(u.GetSystemMetrics(0) // 2, u.GetSystemMetrics(1) - 12)

def get(p):
    return urllib.request.urlopen("http://127.0.0.1:8146" + p, timeout=15).read()

def snap():
    return json.loads(get("/snap").decode())["s"]

def has(n):
    return any(n in (w.get("t") or "") for w in snap() if w.get("ty") != "Splash")

def find(n, exact=False):
    for w in snap():
        if w.get("ty") != "Splash" and w.get("t") is not None:
            t = w["t"]
            if (exact and t == n) or (not exact and n in t):
                x, y, ww, h = w["r"]
                return x + ww // 2, y + h // 2

def state(tag):
    print(f"{tag:26s} reader:{has('AI 摘要')!s:5s} placeholder:{has('选择一封邮件')!s:5s} "
          f"win:{[w['r'] for w in snap() if w.get('ty')=='Window'][0][2]}")

def shot_like():
    get("/m?k=scroll&x=206&y=400&dy=1")
    time.sleep(0.9)
    last = get("/g?raw=1")
    for _ in range(6):
        time.sleep(0.8)
        cur = get("/g?raw=1")
        if cur == last:
            break
        last = cur
    time.sleep(1.2)

state("boot")
shot_like()
state("after shot(01)")

# tap(subject) exactly like drive-demo
pos = find("Re: Q4 联名方案 — 报价确认与签署排期")
get(f"/click?x={pos[0]}&y={pos[1]}&wait=1")
get("/m?k=scroll&x=206&y=400&dy=1")
time.sleep(1.2)
state("after tap(subject)+jiggle")

t0 = time.time()
while time.time() - t0 < 3.0:
    if has("AI 摘要"):
        break
    time.sleep(0.5)
state("after expect poll")

shot_like()
state("after shot(02)")

print("AI 生成 exact:", find("AI 生成", exact=True))
print("AI 生成 substr:", find("AI 生成"))
state("before AI click")
