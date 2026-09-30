#!/usr/bin/env python3
"""Minimal repro: does the shot() jiggle wheel event unselect the mail?"""
import ctypes, json, time, urllib.request

u = ctypes.windll.user32
u.SetCursorPos(u.GetSystemMetrics(0) // 2, u.GetSystemMetrics(1) - 12)

def get(p):
    return urllib.request.urlopen("http://127.0.0.1:8146" + p, timeout=15).read()

def snap():
    return json.loads(get("/snap").decode())["s"]

def has(n):
    return any(n in (w.get("t") or "") for w in snap() if w.get("ty") != "Splash")

def find(n):
    for w in snap():
        if w.get("ty") != "Splash" and w.get("t") and n in w["t"]:
            x, y, ww, h = w["r"]
            return x + ww // 2, y + h // 2

p = find("Re: Q4 联名方案")
get(f"/click?x={p[0]}&y={p[1]}&wait=1")
time.sleep(1.5)
print("after click  reader:", has("AI 摘要"), "| placeholder:", has("选择一封邮件"))

get("/m?k=scroll&x=206&y=400&dy=1")
time.sleep(1.0)
print("after dy=1   reader:", has("AI 摘要"), "| placeholder:", has("选择一封邮件"))

g = get("/g?raw=1")
print("after grab   reader:", has("AI 摘要"), "| placeholder:", has("选择一封邮件"), f"({len(g)}B)")

time.sleep(2.0)
print("after wait   reader:", has("AI 摘要"), "| placeholder:", has("选择一封邮件"))
