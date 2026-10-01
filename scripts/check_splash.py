#!/usr/bin/env python3
"""Quick static sanity for main.splash: brace balance + marker integrity."""
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SRC = r"D:\Coding\Rust\agenticapp26\VibeMail\bundle\main.splash"
src = open(SRC, encoding="utf-8").read()

depth = 0
line = 1
negs = []
for ch in src:
    if ch == "\n":
        line += 1
    elif ch == "{":
        depth += 1
    elif ch == "}":
        depth -= 1
        if depth < 0:
            negs.append(line)
            depth = 0

print("final depth:", depth)
print("negative-depth lines:", negs[:10])
print("total lines:", src.count("\n") + 1)
print("MARKER:ADAPTER blocks:", src.count("MARKER:ADAPTER"))
print("fn count:", src.count("\nfn ") + src.startswith("fn "))
