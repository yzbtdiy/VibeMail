#!/usr/bin/env python3
"""Watch the in-place selection: does it spontaneously revert?"""
import json, time, urllib.request

def snap():
    return json.load(urllib.request.urlopen("http://127.0.0.1:8146/snap"))

def has(n):
    return any(n in (w.get("t") or "") for w in snap()["s"]
               if w.get("ty") != "Splash")

def find(n):
    for w in snap()["s"]:
        if w.get("ty") != "Splash" and w.get("t") and n in w["t"]:
            x, y, ww, h = w["r"]
            return x + ww // 2, y + h // 2

p = find("Re: Q4 联名方案")
urllib.request.urlopen(f"http://127.0.0.1:8146/click?x={p[0]}&y={p[1]}&wait=1")
time.sleep(1.5)
print("t+0  reader:", has("AI 摘要"), "| placeholder:", has("选择一封邮件"))
for i in range(6):
    time.sleep(2)
    print(f"t+{(i+1)*2}s reader:", has("AI 摘要"),
          "| placeholder:", has("选择一封邮件"))
