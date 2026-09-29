#!/usr/bin/env python3
"""Assemble the DEV bundle (bridge adapter) from the shipped one.

The shipped bundle talks to the platform's mail host service (gate-clean).
This script swaps the adapter block (the code between the MARKER:ADAPTER
lines in bundle/main.splash) for dev/adapter-bridge.splash — which speaks to
the local IMAP/SMTP bridge over loopback HTTP — and rewrites the manifest to
`net` + hosts ["127.0.0.1"]. The result lands in build/dev-bundle/ and is
NEVER submitted: the store gate refuses http:// literals in a .splash, and
real mail in a store app belongs to the platform's service.

Usage:
  python scripts/dev_bundle.py            # assemble build/dev-bundle
  python scripts/dev_bundle.py --check    # also verify no http:// remains in bundle/
"""

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUNDLE = ROOT / "bundle"
DEV_ADAPTER = ROOT / "dev" / "adapter-bridge.splash"
OUT = ROOT / "build" / "dev-bundle"

BEGIN = "// MARKER:ADAPTER"
END = "// MARKER:ADAPTER-END"


def assemble():
    src = (BUNDLE / "main.splash").read_text(encoding="utf-8")
    adapter = DEV_ADAPTER.read_text(encoding="utf-8")
    start = src.index(BEGIN)
    # the marker line itself carries the section comment; keep it, swap the body
    head = src[:src.index("\n", start) + 1]
    tail = src[src.index(END):]
    body = adapter[:adapter.index(END)]
    merged = head + body.split("\n", 1)[1] + tail

    shutil.rmtree(OUT, ignore_errors=True)
    shutil.copytree(BUNDLE, OUT)
    (OUT / "main.splash").write_text(merged, encoding="utf-8")

    manifest = json.loads((BUNDLE / "manifest.json").read_text(encoding="utf-8"))
    manifest["capabilities"] = ["model", "net"]
    manifest["network"] = {"hosts": ["127.0.0.1"]}
    manifest.pop("integrity", None)          # card-host --stamp re-adds it
    (OUT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"dev bundle -> {OUT} (net + bridge adapter)")
    return merged


def check_clean():
    leaks = [p.name for p in BUNDLE.rglob("*") if p.is_file()
             and p.suffix in (".splash", ".card", ".json", ".l0", ".octoscript", ".txt", ".md")
             and p.name not in ("listing.json", "manifest.json")
             and ("http://" in p.read_text(encoding="utf-8", errors="ignore"))]
    if leaks:
        print("SHIPPED BUNDLE NOT CLEAN, http:// found in:", leaks)
        sys.exit(1)
    print("shipped bundle clean: no http:// literals outside metadata")


if __name__ == "__main__":
    assemble()
    if "--check" in sys.argv:
        check_clean()
