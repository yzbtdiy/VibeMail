# Demo driver for vibemail: drives the real card-host window over the
# Makepad remote bridge (GET /snap, /click, /t, /m, /g) and captures the
# listing screenshots plus the reply-lifecycle evidence shots.
#
# New deep-space UI: three tabs (收件箱 / 写信 / Agent), the inbox is a
# responsive master-detail, reading opens beside the list, the write tab is
# a centred compose column, the agent tab carries the squad + activity
# stream with approvals.
#
# Bridge quirks this driver works around, observed on the Windows build:
#   - a click issued too soon after a /g grab can be dropped -> every
#     state-changing click is retried until the expected text appears;
#   - the drawn frame lags the widget tree by one redraw        -> shots
#     nudge a 1px scroll and wait for two identical grabs.
#
# Usage: python scripts/drive-demo.py [port]

import ctypes
import json
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8146

# Park the REAL mouse cursor in the screen's bottom-right corner, away from
# the driven window: OS mouse events at the real cursor interleave with the
# bridge's synthetic ones — they steal taps and can drag the window edge.
_user32 = ctypes.windll.user32
_sw, _sh = _user32.GetSystemMetrics(0), _user32.GetSystemMetrics(1)
_user32.SetCursorPos(_sw - 4, _sh - 4)
BASE = f"http://127.0.0.1:{PORT}"
ROOT = Path(__file__).resolve().parent.parent
EVID = ROOT / "evidence"
SHOTS = ROOT / "bundle" / "screenshots"
EVID.mkdir(parents=True, exist_ok=True)

def get(path):
    with urllib.request.urlopen(BASE + path, timeout=15) as r:
        return r.read()

def snap():
    return json.loads(get("/snap").decode("utf-8"))["s"]

def find(text, exact=False):
    for w in snap():
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

def has(text):
    return find(text) is not None

def wait_for(text, timeout=8):
    t0 = time.time()
    while time.time() - t0 < timeout:
        if has(text):
            return
        time.sleep(0.5)
    raise RuntimeError(f"never saw '{text}'")

def settled_pos(text, exact=False, timeout=6.0):
    """Target position once the scroll momentum has stopped moving it.

    Wheel injection via /m?k=scroll arms inertia: content keeps drifting
    after the event, and a click at pre-drift coordinates hits the wrong
    widget. Sample until two reads 0.3s apart agree."""
    t0 = time.time()
    last = find(text, exact)
    while time.time() - t0 < timeout:
        time.sleep(0.3)
        cur = find(text, exact)
        if last and cur and abs(cur[1] - last[1]) < 6 and abs(cur[0] - last[0]) < 6:
            return cur
        last = cur
    return last

def to_top():
    """Scroll the body back to the top. Wheel dy is heavily scaled by the
    host (~0.15x), so a large negative delta is needed; widgets scrolled
    above the viewport are CLIPPED OUT of /snap entirely, which is how
    deep scroll offsets hide targets after screen switches."""
    for _ in range(3):
        get("/m?k=scroll&x=206&y=400&dy=-6000")
        time.sleep(0.4)

def tap(text, exact=False):
    """One tap attempt at the widget's current position, with scroll-to-reach.

    Tall read views push targets both below AND above the viewport, so the
    search scrolls by the target's own position."""
    hit = find(text, exact)
    tries = 0
    # Scrollable body is 29..766; the glass nav bar (776..860) is fixed and
    # perfectly clickable at its own y. Content just above 766 would be
    # swallowed by the nav, so scroll-content targets stay under it.
    def in_range(p):
        return p and (29 < p[1] < 766 or 776 < p[1] < 855)
    while (not in_range(hit)) and tries < 10:
        dy = 420 if (not hit or hit[1] >= 766) else -2400
        get(f"/m?k=scroll&x=206&y=400&dy={dy}")
        time.sleep(0.5)
        hit = find(text, exact)
        tries += 1
    if not in_range(hit):
        raise RuntimeError(f"cannot reach widget '{text}'")
    hit = settled_pos(text, exact)
    cx, cy = hit
    get(f"/click?x={cx:.0f}&y={cy:.0f}&wait=1")
    get("/m?k=scroll&x=206&y=400&dy=1")      # flush one redraw
    time.sleep(1.2)

def search_for(text, exact=False, timeout=0):
    """has() + scroll: /snap only reports VISIBLE widgets, so an expect that
    landed below the fold needs the view scrolled into it."""
    if find(text, exact):
        return True
    t0 = time.time()
    while time.time() - t0 < timeout:
        get("/m?k=scroll&x=206&y=400&dy=620")
        time.sleep(0.7)
        if find(text, exact):
            return True
    return False

def click_expect(target, expect, tries=4, exact=False):
    """Tap `target` until the screen shows `expect` (re-clicking if the
    click is dropped)."""
    for n in range(tries):
        if search_for(expect):
            return
        print(f"  [try {n}] target={target!r} at={find(target, exact)} expect_seen={has(expect)}")
        tap(target, exact=exact)
        if search_for(expect, timeout=5):
            return
    if not search_for(expect):
        raise RuntimeError(f"click '{target}' never produced '{expect}'")

def type_text(text):
    q = urllib.parse.quote(text)
    get(f"/t?t={q}&wait=1")
    time.sleep(0.4)
    print(f"typed '{text}'")
    # Defocus the input: the first click after typing otherwise just clears
    # focus instead of firing the button under it.
    get("/click?x=395&y=60&wait=1")
    time.sleep(0.3)

def shot(path, tries=3):
    """Stable capture: nudge a redraw, keep grabbing until two match."""
    for i in range(tries):
        get("/m?k=scroll&x=206&y=400&dy=1")
        time.sleep(0.9)
        last = get("/g?raw=1")
        stable = False
        for _ in range(6):
            time.sleep(0.8)
            cur = get("/g?raw=1")
            if cur == last:
                stable = True
                break
            last = cur
        if stable:
            Path(path).write_bytes(last)
            time.sleep(1.2)
            print(f"shot -> {path} ({len(last)} bytes)")
            return
    raise RuntimeError(f"frame never settled for {path}")

# ---- listing screenshots + reply lifecycle evidence -------------------------
wait_for("已分诊今日")                                # triage banner booted
# honest practice-mode line — either no mail service answers (card-host
# without one) or an account-less service (the vault exists, empty)
if not has("邮件服务不可用") and not has("未添加邮箱账号"):
    raise RuntimeError("neither practice-mode banner line appeared")
shot(SHOTS / "01-inbox.png")                         # 1 智能收件箱(分诊横幅+优先级行)

click_expect("Re: Q4 联名方案 — 报价确认与签署排期", "‹ 返回")
shot(SHOTS / "02-read.png")                          # 2 阅读 + AI 摘要(练习数据)

# one-shot model call: card-host answers "no service answers" — the honest
# unavailable state is part of the demo (in a Shell with model it succeeds)
click_expect("AI 生成", "模型服务不可用", exact=True)
shot(EVID / "ev-09-summary-model-unavailable.png")
# the model call really happened: the host's refusal text is on screen
assert has("no service answers"), "expected the host's no-service refusal on screen"

# compose: centred column, tone chips, prompt panel; model fallback text
click_expect("✦ AI 帮我回", "回复给: 林晓薇")
assert not has("Re: Re:"), "subject must not stack a second Re:"
click_expect("告诉 AI 你想表达什么", "告诉 AI 你想表达什么")   # focus the input
type_text("确认账期调整,本周五前完成签署")
click_expect("生成草稿", "已回退本地模板", exact=True)
shot(SHOTS / "03-write.png")                         # 3 AI 写信(模型回退本地模板)
shot(EVID / "ev-10-draft-model-fallback.png")

# back to the inbox, attach a one-tap smart reply to mail 0 — the same
# pending -> confirm -> send lifecycle the compose draft would enter
to_top()
click_expect("收件箱", "已分诊今日", exact=True)
click_expect("Re: Q4 联名方案 — 报价确认与签署排期", "‹ 返回")
click_expect("确认条款并安排签署", "回复草稿 · 待发送")      # smart-reply chip
shot(EVID / "ev-01-draft-pending.png")               # draft attached, 待发送

click_expect("发送", "确认发送给", exact=True)
shot(EVID / "ev-02-confirm.png")                     # explicit confirm step

click_expect("确认发送", "已回复 · 刚刚发送", exact=True)
shot(EVID / "ev-03-sent.png")                        # sent strip
to_top()
click_expect("‹ 返回", "已分诊今日")
shot(EVID / "ev-04-inbox-sent-pill.png")             # inbox pill now 已回复

# failure -> keep draft -> retry from the strip (the outage is a practice
# switch, enabled on the write tab BEFORE attaching the reply)
to_top()
click_expect("写信", "回复给:")
click_expect("已关闭", "已开启")                       # enable the outage switch
to_top()
click_expect("收件箱", "已分诊今日", exact=True)
click_expect("终面反馈:高级产品设计师候选人", "‹ 返回")
click_expect("同意录用,不再加面", "回复草稿 · 待发送")   # one-tap smart reply
click_expect("发送", "确认发送给", exact=True)
click_expect("确认发送", "发送失败", exact=True)
shot(EVID / "ev-05-failed.png")                      # send failed, draft kept
click_expect("保留草稿", "回复草稿 · 待发送")
shot(EVID / "ev-06-kept-draft.png")                  # back to 待发送, text intact
to_top()
click_expect("写信", "回复给:")
click_expect("已开启", "已关闭")                       # disable the outage switch
to_top()
click_expect("收件箱", "已分诊今日", exact=True)
click_expect("终面反馈:高级产品设计师候选人", "‹ 返回")
click_expect("发送", "确认发送给", exact=True)
click_expect("确认发送", "已回复 · 刚刚发送", exact=True)
shot(EVID / "ev-07-retry-sent.png")                  # retry succeeds

# agent squad: stats, toggles, live stream, approval
to_top()
click_expect("Agent", "我的 AGENT 小队", exact=True)
click_expect("需审批", "需审批")                       # stream shows pending approvals
click_expect("✓ 批准", "已处理")
shot(EVID / "ev-08-agents-approval.png")
shot(SHOTS / "04-agents.png")                        # 4 Agent 小队(统计+开关+活动流)

(EVID / "final-snap.json").write_bytes(get("/snap"))
(EVID / "final-log.txt").write_bytes(get("/log?n=200"))
print("DONE")
