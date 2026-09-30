#!/usr/bin/env python3
"""Dump all Label/ButtonFlat texts with y positions from /snap."""
import json, sys, urllib.request

PORT = sys.argv[1] if len(sys.argv) > 1 else "8146"
snap = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/snap"))
rows = []
for n in snap.get("s", []):
    t = n.get("t")
    if t and len(t) < 60 and n.get("ty") != "Splash":
        rows.append((n["r"][1], n["r"], t))
rows.sort()
for y, r, t in rows[:40]:
    print(f"y={y:5.0f} r={r} t={t!r}")
