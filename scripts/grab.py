#!/usr/bin/env python3
"""Force a repaint and grab a frame from a makepad remote bridge."""
import sys, time, urllib.request

port, out = sys.argv[1], sys.argv[2]
base = f"http://127.0.0.1:{port}"
urllib.request.urlopen(base + "/m?k=scroll&x=200&y=400&dy=1").read()
time.sleep(0.8)
data = urllib.request.urlopen(base + "/g?raw=1").read()
open(out, "wb").write(data)
print(f"saved {out} {len(data)} bytes")
