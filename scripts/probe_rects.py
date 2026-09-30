#!/usr/bin/env python3
"""Dump key widget rects from /snap (flat list) for layout verification."""
import json, sys, urllib.request

PORT = sys.argv[1] if len(sys.argv) > 1 else "8146"
snap = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/snap"))
print("window:", next((n.get("r") for n in snap.get("s", []) if n.get("ty") == "Window"), None))
for n in snap.get("s", []):
    ty = n.get("ty")
    t = n.get("t") or ""
    if ty == "Splash":
        continue
    if ty in ("RoundedView", "View") and n.get("r") and n["r"][2] > 300:
        print(f"{ty:12s} r={n['r']}")
    elif ty == "Label" and ("选择一封邮件" in t or "智能收件箱" in t or "收件箱" == t):
        print(f"{ty:12s} r={n['r']} t={t[:18]!r}")
    elif ty == "ButtonFlat" and n.get("t") in ("收件箱", "写信", "Agent", "全部 8", "紧急 3"):
        print(f"{ty:12s} r={n['r']} t={n.get('t')!r}")
