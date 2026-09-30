# Official OctoSense mail-sheet flow, scoped to the VibeMail window only:
# the desktop may hold other windows (the system Mail app draws the SAME
# official sheet), so every lookup is constrained to the module rect whose
# card Splash source starts with '// VibeMail'.
import json
import re
import time
import urllib.request
import urllib.parse
from pathlib import Path

BASE = "http://127.0.0.1:8147"
EVID = Path(__file__).resolve().parent.parent / "evidence"

def get(path):
    with urllib.request.urlopen(BASE + path, timeout=25) as r:
        return r.read()

def snap():
    return json.loads(get("/snap").decode("utf-8"))["s"]

def rect_of(w):
    return w["r"]

def inside(w, box):
    x, y, ww, h = rect_of(w)
    bx, by, bw, bh = box
    cx, cy = x + ww / 2, y + h / 2
    return bx <= cx <= bx + bw and by <= cy <= by + bh

def app_box():
    for w in snap():
        if w.get("ty") == "Splash" and w.get("t", "").lstrip().startswith("// VibeMail"):
            return rect_of(w)
    return None

def in_app(ty=None, text=None, exact=True):
    box = app_box()
    if box is None:
        return None
    for w in snap():
        if w.get("ty") == "Splash":
            continue
        if ty and w.get("ty") != ty:
            continue
        t = w.get("t", "")
        if text is not None:
            if (exact and t != text) or (not exact and text not in t):
                continue
        if inside(w, box):
            return w
    return None

def click(w):
    x, y, ww, h = rect_of(w)
    get(f"/click?x={x + ww / 2:.0f}&y={y + h / 2:.0f}&wait=1")
    time.sleep(1.2)

def type_text(text):
    get("/t?t=" + urllib.parse.quote(text) + "&wait=1")
    time.sleep(0.5)

def shot(path):
    get(f"/m?k=scroll&x=600&y=400&dy=1")
    time.sleep(1.0)
    last = get("/g?raw=1")
    for _ in range(6):
        time.sleep(0.8)
        cur = get("/g?raw=1")
        if cur == last:
            Path(path).write_bytes(cur)
            print("shot ->", path, len(cur))
            return
        last = cur
    raise RuntimeError("frame never settled")

box = app_box()
assert box, "VibeMail window not found"
print("VibeMail window:", box)

# 1. come back to the inbox if a detail page is up
for _ in range(3):
    back = in_app(ty="Button", text="‹ 返回")
    if not back:
        break
    click(back)
    time.sleep(1.0)
if not in_app(text="已分诊今日", exact=False):
    nav = in_app(text="收件箱")
    if nav:
        click(nav)
time.sleep(1.5)
assert in_app(text="未添加邮箱账号", exact=False), "banner not visible"
shot(EVID / "ev-17-octosense-app-running.png")

# 2. add-account opens the official sheet (inside the app's area)
for _ in range(5):
    if in_app(text="Add a mail account", exact=False):
        break
    btn = in_app(ty="Button", text="添加账号")
    if btn:
        click(btn)
    time.sleep(1.5)
assert in_app(text="Add a mail account", exact=False), "the official sheet did not open"
time.sleep(1.5)
shot(EVID / "ev-18-octosense-official-sheet.png")

def fields():
    box = app_box()
    return [w for w in snap() if w.get("ty") == "TextInput" and inside(w, box)]

# 3. address + password (empty fields)
for w, text in zip(fields()[:3], ["vibemail.test@qq.com", "", "wrong-code-000"]):
    if text:
        click(w)
        type_text(text)
print("top fields filled:", [w.get("t", "")[:24] for w in fields()[:3]])

# 4. reveal the server rows inside the app area and point them at QQ
for _ in range(8):
    if any("gmail.com" in w.get("t", "") for w in fields()):
        break
    get("/m?k=scroll&x=600&y=420&dy=240&dst=3.0")
    time.sleep(0.9)
for needle, value in [("imap.gmail.com", "imap.qq.com"), ("pop.gmail.com", "imap.qq.com"), ("smtp.gmail.com", "smtp.qq.com")]:
    w = next((c for c in fields() if needle in c.get("t", "")), None)
    if not w:
        print("field not found:", needle)
        continue
    click(w)
    get("/key?c=a&ctrl=1")
    time.sleep(0.4)
    type_text(value)
    print("set", needle, "->", value)
print("server fields:", [w.get("t", "") for w in fields() if "imap" in w.get("t", "") or "smtp" in w.get("t", "")])

# 5. back to the top, submit
for _ in range(6):
    if in_app(ty="Button", text="Sign in"):
        break
    get("/m?k=scroll&x=600&y=420&dy=-240&dst=3.0")
    time.sleep(0.9)
btn = in_app(ty="Button", text="Sign in")
assert btn, "Sign in unreachable"
click(btn)

# 6. the official service answers with the server's own words
HINTS = ("Cannot connect", "Cannot resolve", "rejected the sign-in", "Checking", "Signed in")
status = None
for i in range(60):
    time.sleep(1.0)
    box = app_box() or (0, 0, 1400, 860)
    for w in snap():
        if w.get("ty") != "Label" or not inside(w, box):
            continue
        t = w.get("t", "")
        if any(h in t for h in HINTS):
            status = t
            break
    if status and "Checking" not in status and "Cannot" not in status:
        break
print("STATUS:", status)

shot(EVID / "ev-19-octosense-signin-rejected.png")
(EVID / "ev-octosense-log.txt").write_bytes(get("/log?n=400"))
print("DONE")
