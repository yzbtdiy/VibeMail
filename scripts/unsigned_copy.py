#!/usr/bin/env python3
"""Make an unsigned test copy of bundle/ (strip the publisher signature) so
card-host can run route regression against the same bytes we submit signed."""
import json
import shutil
from pathlib import Path

SRC = Path(r"D:\Coding\Rust\agenticapp26\VibeMail\bundle")
DST = Path(r"D:\Coding\Rust\agenticapp26\VibeMail\build\unsigned-bundle")

if DST.exists():
    shutil.rmtree(DST)
shutil.copytree(SRC, DST)
m = DST / "manifest.json"
d = json.loads(m.read_text(encoding="utf-8"))
removed = d.get("integrity", {}).pop("signature", None)
m.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
print("signature removed:", bool(removed))
