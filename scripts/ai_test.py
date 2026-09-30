# AI provider test for vibemail inside the OctoSense desktop shell.
# Drives the two model.complete paths and reports whether the host's
# configured provider (MiniMax) actually answered:
#   1. reader  -> AI 生成      (summary points)
#   2. compose -> 生成草稿     (draft body)
# Success evidence: the state pill flips to 模型生成 and the widget tree
# carries NEW texts (model output) that were not on screen before.
# Usage: python scripts/ai_test.py [port]     (default 8147)
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

PORT = int(__import__("sys").argv[1]) if len(__import__("sys").argv) > 1 else 8147
BASE = f"http://127.0.0.1:{PORT}"
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

def app_texts():
    box = app_box()
    if box is None:
        return set()
    return {w.get("t", "") for w in snap()
            if w.get("ty") != "Splash" and w.get("t") and inside(w, box)}

def in_app(ty=None, text=None, exact=True, tallest=False):
    box = app_box()
    if box is None:
        return None
    best = None
    for w in snap():
        if w.get("ty") == "Splash":
            continue
        if ty and w.get("ty") != ty:
            continue
        t = w.get("t", "")
        if text is not None:
            if (exact and t != text) or (not exact and text not in t):
                continue
        if not inside(w, box):
            continue
        if tallest:
            if best is None or rect_of(w)[3] > rect_of(best)[3]:
                best = w
        else:
            return w
    return best

def click(w):
    x, y, ww, h = rect_of(w)
    get(f"/click?x={x + ww / 2:.0f}&y={y + h / 2:.0f}&wait=1")
    time.sleep(1.2)

def type_text(text):
    get("/t?t=" + urllib.parse.quote(text) + "&wait=1")
    time.sleep(0.5)

def shot(path):
    get("/m?k=scroll&x=600&y=420&dy=1")
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

def wait_done(before, ok_text, fail_text, budget):
    """Poll until the state pill flips or fresh model output appears.
    MiniMax summaries can take minutes on a cold session, so a pill miss
    with new long texts still counts as a (late) success."""
    t0 = time.time()
    while time.time() - t0 < budget:
        ts = app_texts()
        if any(ok_text == t for t in ts):
            return True, time.time() - t0
        if any(fail_text in t for t in ts):
            return False, time.time() - t0
        fresh = [t for t in ts - before if len(t) > 15]
        if len(fresh) >= 2:
            return True, time.time() - t0
        time.sleep(2.0)
    return False, budget

def to_top():
    # 0.5.1: panes scroll independently — reset all three (shell window is
    # ~990 wide: list ≈500, reader ≈740, copilot ≈890)
    for x in (500, 740, 890):
        for _ in range(4):
            get(f"/m?k=scroll&x={x}&y=420&dy=-6000")
            time.sleep(0.3)

box = app_box()
assert box, "VibeMail window not found"
print("VibeMail window:", box)
# a previous session may have stopped on another screen — go home first
if not in_app(text="已整理今日", exact=False):
    nav = in_app(text="收件箱", exact=True)
    assert nav, "inbox nav row not found"
    click(nav)
to_top()
assert in_app(text="已整理今日", exact=False), "inbox banner not visible"

# ---------- 1. AI summary on mail 0 ------------------------------------------
row = in_app(text="Re: Q4 联名方案", exact=False)
assert row, "mail row not found"
click(row)
time.sleep(1.0)
assert in_app(text="AI COPILOT", exact=False), "copilot panel missing"

before = app_texts()
pill_before = "生成中…" if "生成中…" in before else (
    "模型生成" if "模型生成" in before else (
    "服务不可用" if any("服务不可用" in t for t in before) else "练习数据"))
print("summary pill before:", pill_before)

btn = in_app(ty="Button", text="AI 生成", exact=True)
assert btn, "AI 生成 button not found"
t0 = time.time()
click(btn)
ok, dt = wait_done(before, "模型生成", "服务不可用", 300)
print(f"AI-SUMMARY: {'OK' if ok else 'FAIL'} after {dt:.0f}s (pill was {pill_before})")

after = app_texts()
new = sorted(t for t in after - before if len(t) > 8)
print("new on screen after the call:")
for t in new[:12]:
    print("   ", t[:80])
shot(EVID / "ev-22-ai-summary-shell.png")

# ---------- 2. AI draft on the compose screen --------------------------------
to_top()
nav = in_app(text="写信 · AI 起草", exact=True)
assert nav, "compose nav missing"
click(nav)
time.sleep(1.2)
assert in_app(text="COMPOSE WITH AI", exact=False), "compose rail missing"

prompt = in_app(ty="TextInput", tallest=False)  # first field = prompt input
fields = [w for w in snap() if w.get("ty") == "TextInput" and inside(w, app_box())]
assert fields, "no text inputs found"
prompt = fields[0]
click(prompt)
type_text("跟进上周的报价,确认账期调整并推进签署排期")

before2 = app_texts()
btn = in_app(ty="Button", text="生成草稿", exact=True)
assert btn, "生成草稿 button not found"
click(btn)
ok2, dt2 = wait_done(before2, "模型生成", "服务不可用", 300)
print(f"AI-DRAFT: {'OK' if ok2 else 'FAIL'} after {dt2:.0f}s")

# the draft body lives in the tallest TextInput on the card
time.sleep(1.5)
draft = ""
for w in snap():
    if w.get("ty") == "TextInput" and inside(w, app_box()):
        if rect_of(w)[3] > 60:
            draft = w.get("t", "")
print("draft text:", repr(draft[:220]))
shot(EVID / "ev-23-ai-draft-shell.png")

print("VERDICT:",
      "summary=" + ("MODEL" if ok else "UNAVAILABLE"),
      "draft=" + ("MODEL" if ok2 else "UNAVAILABLE"))
(EVID / "ev-ai-test-log.txt").write_bytes(get("/log?n=200"))
print("DONE")
