#!/usr/bin/env python3
"""VibeMail launcher — one command for every way to run the app.

modes
  mobile   (default) card-host, 412x860 — the phone layout
  desktop  card-host, 1200x860 — inbox/read master-detail
  demo     desktop width + scripts/drive-demo.py: the full evidence run
           (screenshots 01..04 + ev-01..10), fresh instance
  mail     mobile + scripts/drive-mail.py: store-form mail flow
           (no-account -> host sheet -> real imap.qq.com rejection -> cancel)
  shell    the real OctoSense desktop shell with the bundle installed from
           the local signed hub (../octosense-local-hub/device)
  shell-drive  shell + scripts/official_sheet_run.py (the ev-17..19 flow)
  check    service unit tests + hub stamp + hub gate check on bundle/
  stop     kill every test instance (card-host / octosense on 8146/8147)

Every mode cleans the port first, parks the real mouse cursor away from the
driven window (OS cursor events eat the bridge's synthetic taps), waits for
the app to boot, and prints what to do next.
"""

import argparse
import ctypes
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

APP = Path(__file__).resolve().parent.parent          # VibeMail
ROOT = APP.parent                                     # agenticapp26 workspace
HUB = ROOT / "OctoSense-App-Hub"
LOCAL_HUB = ROOT / "octosense-local-hub"

CARD_HOST = os.environ.get(
    "CARD_HOST_EXE",
    r"D:\Users\yzbtdiy\Cache\CARGO_TARGET\release\card-host.exe",
)
OCTOSENSE = os.environ.get(
    "OCTOSENSE_EXE",
    r"D:\Users\yzbtdiy\Cache\CARGO_TARGET\release\octosense.exe",
)
HUB_EXE = os.environ.get("HUB_EXE", str(HUB / "target" / "release" / "hub.exe"))

# The anchor public hex of the local dev hub (octosense-local-hub/README.md).
# OCTOSENSE_HUB_ANCHOR is the documented development-only override.
HUB_ANCHOR = "a7f2748ad5556ecee95931dbbe54857ee138dd34b8e6bb44927db4f7eb7995e2"

MOBILE_PORT = "8146"
SHELL_PORT = "8147"


def sh(cmd, **kw):
    print("+", " ".join(str(c) for c in cmd))
    return subprocess.run([str(c) for c in cmd], **kw)


def kill_port_listeners():
    """Free 8146/8147 and any stray octosense.exe. Failures are fine.
    (netstat/taskkill emit localized GBK text on zh-CN Windows — decode
    loosely.)"""
    def run_dec(cmd):
        return subprocess.run(
            cmd, capture_output=True, text=True,
            encoding="utf-8", errors="replace",
        ).stdout or ""

    out = run_dec(["netstat", "-ano"]).splitlines()
    pids = set()
    for line in out:
        if ("8146" in line or "8147" in line) and "LISTENING" in line:
            pids.add(line.split()[-1])
    for pid in pids:
        run_dec(["taskkill", "/PID", pid, "/F"])
    run_dec(["taskkill", "/im", "octosense.exe", "/F"])
    if pids:
        time.sleep(2)          # let the ports leave TIME_WAIT
    return sorted(pids)


def park_mouse():
    """Move the real cursor to the middle of the taskbar, away from the
    driven window: OS mouse events at the real cursor interleave with the
    bridge's synthetic ones and steal taps — and a cursor parked on a screen
    CORNER sits on a window resize grip and DRAGS the window narrower (seen
    as mid-run window resizes). The taskbar centre has no window edge."""
    u = ctypes.windll.user32
    u.SetCursorPos(u.GetSystemMetrics(0) // 2, u.GetSystemMetrics(1) - 12)


def wait_up(port, timeout=25):
    """Poll the bridge until the app answers."""
    base = f"http://127.0.0.1:{port}"
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            urllib.request.urlopen(base + "/log?n=1", timeout=3).read()
            return True
        except OSError:
            time.sleep(0.5)
    return False


def wait_card_booted(port, timeout=25):
    """The bridge answers before the card renders; wait for the greeting
    text to exist in the widget tree."""
    base = f"http://127.0.0.1:{port}"
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            import json
            snap = json.loads(
                urllib.request.urlopen(base + "/snap", timeout=3).read()
            )
            for w in snap.get("s", []):
                t = w.get("t") or ""
                if w.get("ty") != "Splash" and ("未读邮件" in t or "未添加邮箱账号" in t):
                    return True
        except OSError:
            pass
        time.sleep(0.6)
    return False


def make_run_bundle():
    """card-host --allow-unsigned refuses SIGNED manifests (it installs no
    verifier), so runs always target a refreshed unsigned copy of bundle/;
    the submitted bundle keeps its publisher signature."""
    import json
    src, dst = APP / "bundle", APP / "build" / "run-bundle"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    m = dst / "manifest.json"
    d = json.loads(m.read_text(encoding="utf-8"))
    d.get("integrity", {}).pop("signature", None)
    m.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    return dst


def launch_card_host(width, height, port=MOBILE_PORT):
    if not Path(CARD_HOST).exists():
        sys.exit(f"card-host not found: {CARD_HOST} (build it: "
                 f"cd {HUB} && cargo build --release -p octosense-card-host, "
                 f"or set CARD_HOST_EXE)")
    run_bundle = make_run_bundle()
    env = dict(os.environ, MAKEPAD_REMOTE=port)
    exe = subprocess.Popen(
        [CARD_HOST, "--bundle", str(run_bundle), "--app-data", ".local-state",
         "--allow-unsigned", "--stamp", "--size", f"{width}x{height}"],
        cwd=APP, env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
    )
    print(f"card-host pid {exe.pid} on :{port} at {width}x{height} "
          f"(bundle: {run_bundle})")
    if not wait_up(port) or not wait_card_booted(port):
        sys.exit("card-host did not boot (see the window / try `run.cmd stop`)")
    return exe


def launch_shell(drive=False):
    if not Path(OCTOSENSE).exists():
        sys.exit(f"octosense.exe not found: {OCTOSENSE} (build it per "
                 f"../octosense-local-hub/README.md, or set OCTOSENSE_EXE)")
    device = LOCAL_HUB / "device"
    if not (device / "vibemail" / "bundle").exists():
        sys.exit(f"no install layout under {device} — republish first "
                 f"(../octosense-local-hub/README.md)")
    env = dict(
        os.environ,
        MAKEPAD_REMOTE=SHELL_PORT,
        OCTOSENSE_HUB_ANCHOR=HUB_ANCHOR,
        OCTOSENSE_APP_DATA=str(device),
    )
    exe = subprocess.Popen(
        [OCTOSENSE, "--test-action", "launch-hub:vibemail"],
        cwd=LOCAL_HUB, env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
    )
    print(f"octosense pid {exe.pid} on :{SHELL_PORT} "
          f"(wm: launched hub:vibemail)")
    if not wait_up(SHELL_PORT, timeout=40):
        sys.exit("the shell bridge did not come up")
    time.sleep(6)          # the card takes a moment to launch as a client
    if drive:
        park_mouse()
        r = sh([sys.executable, APP / "scripts" / "official_sheet_run.py"])
        sys.exit(r.returncode)
    print("shell is up; drive the official-sheet flow with:")
    print(f"  python scripts/official_sheet_run.py   (MAKEPAD_REMOTE={SHELL_PORT})")
    return exe


def main():
    ap = argparse.ArgumentParser(prog="run.cmd", add_help=True,
                                 description=__doc__.splitlines()[1])
    ap.add_argument("mode", nargs="?", default="desktop",
                    choices=["mobile", "desktop", "demo", "mail",
                             "shell", "shell-drive", "check", "stop"])
    args = ap.parse_args()

    if args.mode == "stop":
        killed = kill_port_listeners()
        print("stopped:", killed or "nothing was listening")
        return

    if args.mode == "check":
        r = sh([sys.executable, "-m", "unittest", "discover", "-s", "service"],
               cwd=APP)
        if r.returncode:
            sys.exit("unit tests failed")
        sh([HUB_EXE, "stamp", "bundle"], cwd=APP)
        sh([HUB_EXE, "check", "bundle", "--allow-unsigned"], cwd=APP)
        return

    kill_port_listeners()
    park_mouse()

    if args.mode == "shell":
        launch_shell(drive=False)
        return
    if args.mode == "shell-drive":
        launch_shell(drive=True)
        return

    # demo drives the store-form phone column (wheel anchor x=206, screenshot
    # geometry 412x860 — the shipped shots are 824x1720 @2x): mobile width
    width, height = (412, 860) if args.mode in ("mobile", "demo") else (1200, 860)
    launch_card_host(width, height)

    if args.mode in ("demo", "mail"):
        driver = ("drive-demo.py" if args.mode == "demo" else "drive-mail.py")
        park_mouse()
        r = sh([sys.executable, APP / "scripts" / driver, MOBILE_PORT])
        sys.exit(r.returncode)

    print(f"app is up on :{MOBILE_PORT} ({width}x{height}) — click the window, or")
    print("  run.cmd demo   full evidence run (01..04 + ev-01..10)")
    print("  run.cmd mail   store-form mail flow (host sheet, real rejection)")
    print("  run.cmd stop   when done")


if __name__ == "__main__":
    main()
