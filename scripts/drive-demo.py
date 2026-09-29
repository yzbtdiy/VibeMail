# Demo driver for agentic-mail: drives the real card-host window over the
# Makepad remote bridge (GET /snap, /click, /t, /m, /g) and captures the
# listing screenshots plus the reply-lifecycle evidence shots.
#
# Bridge quirks this driver works around, observed on the Windows build:
#   - a click issued too soon after a /g grab can be dropped -> every
#     state-changing click is retried until the expected text appears;
#   - the drawn frame lags the widget tree by one redraw        -> shots
#     nudge a 1px scroll and wait for two identical grabs.
#
# Usage: python build/drive-demo.py [port]

import json
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8145
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

def tap(text, exact=False):
    """One tap attempt at the widget's current position, with scroll-to-reach."""
    hit = find(text, exact)
    tries = 0
    while (not hit or not (29 < hit[1] < 850)) and tries < 6:
        get("/m?k=scroll&x=206&y=400&dy=420")
        time.sleep(0.5)
        hit = find(text, exact)
        tries += 1
    if not hit or not (29 < hit[1] < 850):
        raise RuntimeError(f"cannot reach widget '{text}'")
    cx, cy = hit
    get(f"/click?x={cx:.0f}&y={cy:.0f}&wait=1")
    get("/m?k=scroll&x=206&y=400&dy=1")      # flush one redraw
    time.sleep(1.2)

def click_expect(target, expect, tries=4, exact=False):
    """Tap `target` until the screen shows `expect` (re-clicking if the
    click is dropped)."""
    for _ in range(tries):
        if has(expect):
            return
        tap(target, exact=exact)
        t0 = time.time()
        while time.time() - t0 < 3.0:
            if has(expect):
                return
            time.sleep(0.5)
    if not has(expect):
        raise RuntimeError(f"click '{target}' never produced '{expect}'")

def type_text(text):
    q = urllib.parse.quote(text)
    get(f"/t?t={q}&wait=1")
    time.sleep(0.4)
    print(f"typed '{text}'")

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
wait_for("AI 分诊")
shot(SHOTS / "01-inbox.png")                        # 1 智能收件箱

click_expect("【紧急】产品发布会流程确认", "邮件详情")
shot(SHOTS / "02-read.png")                         # 2 邮件阅读 + AI 摘要(练习数据)

# one-shot model call: card-host answers "no service answers" — the honest
# unavailable state is part of the demo (in a Shell with model it succeeds)
click_expect("AI 生成", "模型服务不可用", exact=True)
shot(EVID / "ev-09-summary-model-unavailable.png")

click_expect("回复", "写邮件", exact=True)
click_expect("告诉 AI 你想表达什么", "告诉 AI 你想表达什么")   # focus the input
type_text("确认发布会流程,按当前版本执行")
click_expect("重新生成", "模型服务不可用")
shot(SHOTS / "03-write.png")                        # 3 AI 写信起草(模型回退本地模板)
shot(EVID / "ev-10-draft-model-fallback.png")

click_expect("插入并发送", "回复草稿 · 待发送")
shot(EVID / "ev-01-draft-pending.png")              # draft attached, 待发送

click_expect("发送", "确认发送给", exact=True)
shot(EVID / "ev-02-confirm.png")                    # explicit confirm step

click_expect("确认发送", "已回复 · 刚刚发送", exact=True)
shot(EVID / "ev-03-sent.png")                       # sent strip
click_expect("‹ 返回", "AI 分诊")
shot(EVID / "ev-04-inbox-sent-pill.png")            # inbox pill now 已回复

# failure -> keep draft -> edit -> resend (the outage is a practice switch)
click_expect("Q2 市场推广方案终稿", "邮件详情")
click_expect("回复", "写邮件", exact=True)
click_expect("已关闭", "已开启")                      # enable the outage switch
click_expect("插入并发送", "回复草稿 · 待发送")
click_expect("发送", "确认发送给", exact=True)
click_expect("确认发送", "发送失败", exact=True)
shot(EVID / "ev-05-failed.png")                      # send failed, draft kept
click_expect("保留草稿", "回复草稿 · 待发送")
shot(EVID / "ev-06-kept-draft.png")                  # back to 待发送, text intact
click_expect("继续编辑", "写邮件")
click_expect("已开启", "已关闭")                      # disable the outage switch
click_expect("插入并发送", "回复草稿 · 待发送")
click_expect("发送", "确认发送给", exact=True)
click_expect("确认发送", "已回复 · 刚刚发送", exact=True)
shot(EVID / "ev-07-retry-sent.png")                  # retry succeeds

click_expect("‹ 返回", "AI 分诊")
click_expect("待办", "待办与跟进", exact=True)
shot(SHOTS / "04-todo.png")                          # 4 跟进提醒待办
click_expect("已完成", "官网改版设计稿确认", exact=True)
shot(EVID / "ev-08-todo-tab-done.png")
click_expect("待跟进", "产品发布会流程确认", exact=True)

click_expect("我的", "概念演示", exact=True)
shot(SHOTS / "05-me.png")                            # 5 我的 + 演示披露

(EVID / "final-snap.json").write_bytes(get("/snap"))
(EVID / "final-log.txt").write_bytes(get("/log?n=200"))
# the model call really happened: the host's refusal text is on screen
assert has("no service answers"), "expected the host's no-service refusal on screen"
print("DONE")
