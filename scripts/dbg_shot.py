#!/usr/bin/env python3
"""Stable desktop shot: open mail, wait for settle, verify tree, grab."""
import ctypes, json, time, urllib.request

port, out = sys.argv if False else ("8147", r"D:\Coding\Rust\agenticapp26\agentic-mail-card\evidence\ev-20-desktop-master-detail.png")
base = f"http://127.0.0.1:{port}"
ctypes.windll.user32.SetCursorPos(3800, 200)

def get(p):
    return urllib.request.urlopen(base + p, timeout=15).read()

def snap():
    return json.loads(get("/snap").decode("utf-8"))["s"]

def find(text):
    for w in snap():
        if w.get("ty") == "Splash":
            continue
        if w.get("t") and text in w["t"]:
            return w["r"]

# go to inbox first (nav), then open the mail
r = find("收件箱")
get(f"/click?x={r[0]+r[2]//2}&y={r[1]+r[3]//2}&wait=1")
time.sleep(1.5)
r = find("Re: Q4 联名方案")
get(f"/click?x={r[0]+r[2]//2}&y={r[1]+r[3]//2}&wait=1")
time.sleep(2.5)
assert find("AI 摘要"), "reader not open"
assert find("选择一封邮件") is None, "still placeholder?"
print("reader open, subject visible")
get("/m?k=scroll&x=600&y=400&dy=1")
time.sleep(1.0)
data = get("/g?raw=1")
open(out, "wb").write(data)
print(f"saved {out} {len(data)}")
