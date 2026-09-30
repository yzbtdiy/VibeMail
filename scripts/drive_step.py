#!/usr/bin/env python3
"""Click the widget whose Label text matches, then grab a frame.

usage: drive_step.py <port> <label-text> <out.png>
"""
import json, sys, time, urllib.request

port, text, out = sys.argv[1], sys.argv[2], sys.argv[3]
base = f"http://127.0.0.1:{port}"

snap = json.load(urllib.request.urlopen(base + "/snap"))
target = None
for n in snap.get("s", []):
    if n.get("ty") == "Splash":
        continue
    if n.get("ty") == "Label" and n.get("t") == text and n.get("r"):
        target = n["r"]
        break
if not target:
    print(f"NOT FOUND: {text!r}")
    sys.exit(1)
x = target[0] + target[2] // 2
y = target[1] + target[3] // 2
print(f"click {text!r} at ({x},{y})")
urllib.request.urlopen(base + f"/click?x={x}&y={y}").read()
time.sleep(1.2)
urllib.request.urlopen(base + "/m?k=scroll&x=200&y=400&dy=1").read()
time.sleep(0.6)
data = urllib.request.urlopen(base + "/g?raw=1").read()
open(out, "wb").write(data)
print(f"saved {out} {len(data)} bytes")
