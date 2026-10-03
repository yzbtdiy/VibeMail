#!/usr/bin/env python3
"""Route runner for vibemail: executes the declarative routes in
route_test.json against a running card-host over the Makepad remote bridge
(GET /snap, /click, /t, /m, /g), in the spirit of the
OctoScript-App-Design-Flow examples' shared route runner: the JSON names
WHAT must happen, this script owns HOW.

Bridge quirks this runner works around (all proven by drive-demo.py on the
Windows build):
  - a click issued too soon after a /g grab can be dropped -> every
    state-changing tap retries until the expected text appears;
  - /snap reports only VISIBLE widgets -> taps scroll targets back into
    range, expects hunt up/down for text landed outside the viewport;
  - wheel injection arms scroll inertia -> click positions settle before
    the tap fires.

On any failure it writes evidence/routes/<route>/<step>/{fail.png,
snap.json, log.txt} and exits 1. It never writes into bundle/.

Usage: python scripts/run_routes.py [port] [--routes PATH] [--only NAME]
Start the app first (run.cmd mobile, or any card-host with MAKEPAD_REMOTE).
"""

import argparse
import ctypes
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

APP = Path(__file__).resolve().parent.parent
EVID = APP / "evidence" / "routes"


# ---- bridge ----------------------------------------------------------------

def get(base, path):
    with urllib.request.urlopen(base + path, timeout=15) as r:
        return r.read()


def snap(base):
    return json.loads(get(base, "/snap").decode("utf-8"))["s"]


def find(base, text, exact=False):
    for w in snap(base):
        # ty "Splash" carries the WHOLE PROGRAM SOURCE as its text — it
        # substring-matches every string in the app and its rect is the full
        # window, so it must never be a click target.
        if w.get("ty") == "Splash":
            continue
        t = w.get("t", "")
        if (exact and t == text) or (not exact and text in t):
            x, y, ww, h = w["r"]
            return x + ww / 2, y + h / 2
    return None


def has(base, text, exact=False):
    return find(base, text, exact) is not None


def wait_for(base, text, timeout=8):
    t0 = time.time()
    while time.time() - t0 < timeout:
        if has(base, text):
            return
        time.sleep(0.5)
    raise RouteError(f"never saw '{text}'")


def settled_pos(base, text, exact=False, timeout=6.0):
    """Target position once the scroll momentum has stopped moving it."""
    t0 = time.time()
    last = find(base, text, exact)
    while time.time() - t0 < timeout:
        time.sleep(0.3)
        cur = find(base, text, exact)
        if last and cur and abs(cur[1] - last[1]) < 6 and abs(cur[0] - last[0]) < 6:
            return cur
        last = cur
    return last


def wheel_x(hit):
    """Wheel x for the pane containing the target — the 0.7.0 phone column
    has ONE scroll body centred at x=206."""
    return 206


def to_top(base):
    """Scroll the phone body back to the top (wheel dy is heavily scaled by
    the host; widgets scrolled out of the viewport are clipped from /snap)."""
    for _ in range(3):
        get(base, "/m?k=scroll&x=206&y=400&dy=-6000")
        time.sleep(0.3)


def tap(base, text, exact=False):
    """One tap attempt at the widget's current position, with scroll-to-reach."""
    hit = find(base, text, exact)
    tries = 0
    # Phone layout: no status bar (removed after 0.7.0's first cut), the
    # detail back row starts at y~12, scrollable screens run to ~792, the
    # docked nav pill sits ~792..860 (in flow — taps fall through every
    # overlapping GestureView, so the pill must not overlay cards).
    def in_range(p):
        return p and 8 < p[1] < 856
    while (not in_range(hit)) and tries < 10:
        dy = 420 if (not hit or hit[1] >= 792) else -2400
        get(base, f"/m?k=scroll&x=206&y=400&dy={dy}")
        time.sleep(0.5)
        hit = find(base, text, exact)
        tries += 1
    if not in_range(hit):
        raise RouteError(f"cannot reach widget '{text}'")
    hit = settled_pos(base, text, exact)
    cx, cy = hit
    get(base, f"/click?x={cx:.0f}&y={cy:.0f}&wait=1")
    get(base, "/m?k=scroll&x=206&y=400&dy=1")      # flush one redraw
    time.sleep(1.2)


def search_for(base, text, exact=False, timeout=0):
    """has() + scroll: the target may sit outside the viewport, above or
    below. Hunt: steady +420 steps (the same reach tap() uses) with a hard
    up-scroll every 4th step — 0.7.1's taller cards need several steps to
    expose a bottom-of-list chip row, which the old ±620 alternation
    (net one weak step per cycle) stalled on."""
    if find(base, text, exact):
        return True
    t0 = time.time()
    n = 0
    while time.time() - t0 < timeout:
        dy = -2400 if n % 4 == 3 else 420
        get(base, f"/m?k=scroll&x=206&y=400&dy={dy}")
        time.sleep(0.7)
        if find(base, text, exact):
            return True
        n += 1
    return False


def click_expect(base, target, expect, tries=4, exact=False):
    """Tap `target` until the screen shows `expect` (re-clicking if the
    click is dropped)."""
    for n in range(tries):
        if search_for(base, expect):
            return
        tap(base, target, exact=exact)
        if search_for(base, expect, timeout=5):
            return
    if not search_for(base, expect):
        raise RouteError(f"click '{target}' never produced '{expect}'")


def type_text(base, text):
    q = urllib.parse.quote(text)
    get(base, f"/t?t={q}&wait=1")
    time.sleep(0.4)
    # Defocus the input: the first click after typing otherwise just clears
    # focus instead of firing the button under it.
    get(base, "/click?x=395&y=60&wait=1")
    time.sleep(0.3)


def check_absent(base, texts):
    for t in texts:
        if has(base, t):
            raise RouteError(f"forbidden text '{t}' is visible")


def check_asserts(base, texts):
    for t in texts:
        if not search_for(base, t, timeout=6):
            raise RouteError(f"expected text '{t}' not found")


# ---- runner ----------------------------------------------------------------

class RouteError(RuntimeError):
    pass


def park_mouse():
    """Windows only: move the real cursor to the taskbar centre, away from
    the driven window — OS cursor events at the real cursor steal the
    bridge's synthetic taps, and a screen-corner cursor drags the resize
    grip. No-op elsewhere."""
    if sys.platform != "win32":
        return
    u = ctypes.windll.user32
    u.SetCursorPos(u.GetSystemMetrics(0) // 2, u.GetSystemMetrics(1) - 12)


def slug(s):
    return re.sub(r"[^0-9A-Za-z_.-]+", "_", s)[:60]


def dump_failure(base, route_dir, step_no, why):
    step_dir = route_dir / f"step-{step_no:02d}"
    step_dir.mkdir(parents=True, exist_ok=True)
    try:
        (step_dir / "fail.png").write_bytes(get(base, "/g?raw=1"))
    except OSError:
        pass
    try:
        (step_dir / "snap.json").write_bytes(get(base, "/snap"))
    except OSError:
        pass
    try:
        (step_dir / "log.txt").write_bytes(get(base, "/log?n=80"))
    except OSError:
        pass
    print(f"    FAILURE at step {step_no}: {why}")
    print(f"    evidence -> {step_dir}")


def run_step(base, step):
    if step.get("scroll_top"):
        to_top(base)
    if "type" in step:
        type_text(base, step["type"])
    if "tap" in step:
        click_expect(base, step["tap"], step.get("expect", step["tap"]),
                     exact=step.get("exact", False))
    elif "tap_offset" in step:
        spec = step["tap_offset"]
        pos = find(base, spec["find"])
        if not pos:
            raise RouteError(f"anchor widget '{spec['find']}' not found")
        get(base, f"/click?x={pos[0] + spec.get('dx', 0):.0f}"
                  f"&y={pos[1] + spec.get('dy', 0):.0f}&wait=1")
        get(base, "/m?k=scroll&x=700&y=400&dy=1")
        time.sleep(1.5)
        if "expect" in step and not search_for(base, step["expect"], timeout=5):
            raise RouteError(f"offset tap never produced '{step['expect']}'")
    if "asserts" in step:
        check_asserts(base, step["asserts"])
    if "absent" in step:
        check_absent(base, step["absent"])


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("port", nargs="?", default="8146")
    ap.add_argument("--routes", default=str(APP / "route_test.json"))
    ap.add_argument("--only", help="run only the route with this name")
    args = ap.parse_args()

    spec = json.loads(Path(args.routes).read_text(encoding="utf-8"))
    base = f"http://127.0.0.1:{args.port}"

    park_mouse()

    boot = spec.get("boot", {})
    print(f"[boot] waiting for '{boot.get('wait_for', 'any widget')}' on {base}")
    wait_for(base, boot["wait_for"], timeout=25)
    banners = boot.get("practice_banner_any", [])
    if banners and not any(has(base, b) for b in banners):
        raise SystemExit(f"[boot] none of the practice-mode banners appeared: {banners}")
    check_asserts(base, boot.get("asserts", []))
    print("[boot] ok")

    routes = spec["routes"]
    if args.only:
        routes = [r for r in routes if r["name"] == args.only]
        if not routes:
            raise SystemExit(f"no route named '{args.only}'")

    failed = 0
    for idx, route in enumerate(routes, 1):
        name = route.get("name", f"route-{idx}")
        desc = route.get("desc", "")
        print(f"\n[{idx}/{len(routes)}] {name}" + (f" — {desc}" if desc else ""))
        for step_no, step in enumerate(route["steps"], 1):
            label = step.get("tap") or step.get("tap_offset", {}).get("find") \
                or step.get("type") or "check"
            print(f"  step {step_no:02d}: {label}")
            try:
                run_step(base, step)
            except RouteError as e:
                dump_failure(base, EVID / f"{idx:02d}-{slug(name)}", step_no, e)
                failed += 1
                break
        else:
            print(f"  PASS ({len(route['steps'])} steps)")

    total = len(routes)
    passed = total - failed
    print(f"\n{passed}/{total} routes passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
