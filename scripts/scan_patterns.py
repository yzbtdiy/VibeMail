#!/usr/bin/env python3
"""Scan main.splash for the squeeze pattern: a width:Fill sibling directly
followed by a Fit-width widget in the same Right row (the trailing widget
gets squeezed to slivers or vanishes on narrow widths)."""
import re
import sys
from pathlib import Path

src = Path(sys.argv[1] if len(sys.argv) > 1 else
           Path(__file__).resolve().parent.parent / "bundle" / "main.splash"
           ).read_text(encoding="utf-8").splitlines()

for i in range(len(src) - 1):
    a, b = src[i], src[i + 1]
    if re.search(r"width: Fill", a) and not re.search(r"width: (Fill|\d)", b):
        if re.match(r"\s*(Label|ButtonFlat|RoundedView|chip)\{", b):
            print(f"{i + 2}: FILL> {b.strip()[:72]}")
