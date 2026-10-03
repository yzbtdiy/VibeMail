# Store-form mail service driver: drives the shipped bundle in card-host
# (with the mail host service registered) through the no-account state, the
# sign-in sheet the service raises, a rejected sign-in and a cancel.
#
# Usage: python scripts/drive-mail.py [port]

import json
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8146
BASE = f"http://127.0.0.1:{PORT}"
ROOT = Path(__file__).resolve().parent.parent
EVID = ROOT / "evidence"
EVID.mkdir(parents=True, exist_ok=True)

def get(path):
    with urllib.request.urlopen(BASE + path, timeout=20) as r:
        return r.read()

def snap():
    return json.loads(get("/snap").decode("utf-8"))["s"]

def find(text, exact=False):
    for w in snap():
        if w.get("ty") == "Splash":
            continue  # its "t" is the whole program source; it swallows every match
        t = w.get("t", "")
        if (exact and t == text) or (not exact and text in t):
            x, y, ww, h = w["r"]
            return x + ww / 2, y + h / 2
    return None

def has(text):
    return find(text) is not None

def wait_for_any(texts, timeout=20):
    t0 = time.time()
    while time.time() - t0 < timeout:
        for t in texts:
            if has(t):
                return t
        time.sleep(0.5)
    raise RuntimeError(f"never saw any of {texts}")

def tap(text, exact=False):
    hit = find(text, exact)
    if not hit:
        raise RuntimeError(f"widget '{text}' not on screen")
    cx, cy = hit
    if not (29 < cy < 850):
        raise RuntimeError(f"widget '{text}' out of reach at {cy}")
    get(f"/click?x={cx:.0f}&y={cy:.0f}&wait=1")
    get("/m?k=scroll&x=206&y=400&dy=1")
    time.sleep(1.2)

def click_expect(target, expects, tries=4, exact=False):
    if isinstance(expects, str):
        expects = [expects]
    for _ in range(tries):
        for e in expects:
            if has(e):
                return
        try:
            tap(target, exact=exact)
        except RuntimeError:
            pass
        t0 = time.time()
        while time.time() - t0 < 3.0:
            for e in expects:
                if has(e):
                    return
            time.sleep(0.5)
    if not any(has(e) for e in expects):
        raise RuntimeError(f"click '{target}' never produced {expects}")

def type_text(text):
    q = urllib.parse.quote(text)
    get(f"/t?t={q}&wait=1")
    time.sleep(0.4)

def shot(path, tries=3):
    for i in range(tries):
        get("/m?k=scroll&x=206&y=400&dy=1")
        time.sleep(0.9)
        last = get("/g?raw=1")
        for _ in range(6):
            time.sleep(0.8)
            cur = get("/g?raw=1")
            if cur == last:
                Path(path).write_bytes(last)
                time.sleep(1.2)
                print(f"shot -> {path} ({len(last)} bytes)")
                return
            last = cur
    raise RuntimeError(f"frame never settled for {path}")

# ---- the store form with the platform mail service -------------------------

def text_inputs():
    return [w for w in snap() if w.get("ty") == "TextInput"]

# Back to the inbox first (a stray tap may have opened the detail page).
if has("AI 三行摘要"):
    tap("收件箱", exact=True)
# A leftover sheet from an earlier run would swallow every tap.
if has("授权码"):
    tap("取消", exact=True)
    time.sleep(1.5)

# The digest line no longer says the service is missing: the mail family is
# registered, there simply is no account yet.
wait_for_any(["未添加邮箱账号", "no service"], timeout=30)
assert has("未添加邮箱账号"), "expected the no-account state, not a missing service"
time.sleep(2.0)  # clicks right after /g grabs get dropped by the bridge
shot(EVID / "ev-13-storeform-no-account.png")

# Mailbox management lives on the 我的 screen (0.7.0): the 添加账号 button
# raises the host's own sign-in sheet. Wait for the sheet's TextInputs
# WITHOUT scrolling — scroll gestures can dismiss the sheet mid-rise, and no
# app-side text is a safe expect (the sheet's own placeholders are the only
# TextInputs on screen).
time.sleep(2.0)
click_expect("我的", ["外观主题"], exact=True)
btn = find("添加账号")
assert btn, "添加账号 button not found on the settings screen"
get(f"/click?x={btn[0]:.0f}&y={btn[1]:.0f}&wait=1")
t0 = time.time()
while time.time() - t0 < 20:
    if any(w.get("ty") == "TextInput" for w in snap()):
        break
    time.sleep(1.0)
shot(EVID / "ev-14-sheet-signin.png")

# A rejected sign-in: the service tests the credentials against the real
# IMAP server and the sheet shows its refusal, staying up for a retry.
inputs = []
for _ in range(10):           # the sheet's inputs can lag the sheet frame
    inputs = text_inputs()
    if len(inputs) >= 2:
        break
    time.sleep(1.0)
assert len(inputs) >= 2, f"expected the sheet's two text inputs, got {len(inputs)}"
for w, text in zip(inputs[:2], ["agentic.mail.test@qq.com", "wrong-code-000"]):
    x, y, ww, h = w["r"]
    get(f"/click?x={x + 60:.0f}&y={y + h / 2:.0f}&wait=1")
    time.sleep(0.6)
    type_text(text)
time.sleep(1.0)
click_expect("登录", ["被拒绝", "无法连接", "失败", "无效", "请输入", "正在登录"], tries=3, exact=True)
shot(EVID / "ev-15-sheet-rejected.png")

# Cancel answers the app's add_account with an error and drops the sheet.
t0 = time.time()
while has("授权码") and time.time() - t0 < 10:
    try:
        tap("取消", exact=True)
    except RuntimeError:
        pass
    time.sleep(1.0)
assert not has("授权码"), "the sheet should be gone"
# a click that fell through the closing sheet may have opened a mail; come
# back to the inbox so the digest line is on screen
for _ in range(3):
    if not has("AI 三行摘要"):
        break
    tap("收件箱", exact=True)
    time.sleep(1.0)
wait_for_any(["未添加邮箱账号"], timeout=10)
shot(EVID / "ev-16-cancelled-back-to-no-account.png")

(EVID / "ev-mail-log.txt").write_bytes(get("/log?n=300"))
print("DONE")
