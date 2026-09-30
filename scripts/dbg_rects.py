#!/usr/bin/env python3
"""Print rects of several texts from /snap."""
import json, sys, urllib.request

port = sys.argv[1]
texts = sys.argv[2:]
snap = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/snap"))
for n in snap.get("s", []):
    t = n.get("t")
    if t and any(t == w or (w in t and len(w) > 3) for w in texts):
        print(f"{n.get('ty'):12s} r={n['r']} t={t[:30]!r}")
