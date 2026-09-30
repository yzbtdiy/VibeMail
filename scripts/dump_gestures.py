#!/usr/bin/env python3
"""Dump every GestureView rect from /snap."""
import json, sys, urllib.request

PORT = sys.argv[1] if len(sys.argv) > 1 else "8146"
snap = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/snap"))
for n in snap.get("s", []):
    if n.get("ty") == "GestureView":
        print(f"r={n.get('r')}")
