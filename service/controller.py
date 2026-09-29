"""Reply-lifecycle reducer for agentic-mail.

This module is the verification twin of the state machine implemented in
``bundle/main.splash`` (functions ``insert_draft`` / ``ask_send`` /
``cancel_send`` / ``do_send`` / ``finish_send`` / ``retry_send`` /
``keep_draft`` / ``edit_draft`` / ``quick_reply``). The Splash runtime has no
unit-test harness of its own, so the transitions live here as plain Python
and are exercised by ``test_controller.py``; ``scripts/drive-demo.py`` then
performs the exact same route against the real card-host window. The three
must stay in step — a transition added to the UI belongs here too.

State machine (per mail object):

    ""  --attach_draft-->  pending
    pending --ask_send-->  confirm --cancel_send--> pending
    confirm --do_send-->   sending --(timer, outage?)--> sent | failed
    failed --retry_send--> sending (same finish rule)
    failed --keep_draft--> pending
    pending --edit_draft--> (draft editing; still pending)

Nothing here talks to a real mail service: ``send`` is simulated, exactly as
the UI discloses (practice data).
"""

PENDING = "pending"
CONFIRM = "confirm"
SENDING = "sending"
SENT = "sent"
FAILED = "failed"

VALID_REPLY_STATES = ("", PENDING, CONFIRM, SENDING, SENT, FAILED)


def initial_state():
    """One mail's reply state, mirroring a ``mails[i]`` literal in main.splash."""
    return {"reply": "", "reply_text": "", "outage": False}


def attach_draft(state, text):
    if not text:
        raise ValueError("empty draft")
    state["reply_text"] = text
    state["reply"] = PENDING
    return state


def ask_send(state):
    if state["reply"] != PENDING:
        raise ValueError(f"ask_send from {state['reply']!r}")
    state["reply"] = CONFIRM
    return state


def cancel_send(state):
    if state["reply"] != CONFIRM:
        raise ValueError(f"cancel_send from {state['reply']!r}")
    state["reply"] = PENDING
    return state


def do_send(state):
    """The user confirmed; the UI starts a 0.9 s timer, then finish_send."""
    if state["reply"] not in (CONFIRM, FAILED):
        raise ValueError(f"do_send from {state['reply']!r}")
    state["reply"] = SENDING
    return state


def finish_send(state):
    if state["reply"] != SENDING:
        raise ValueError(f"finish_send from {state['reply']!r}")
    state["reply"] = FAILED if state["outage"] else SENT
    return state


def retry_send(state):
    return do_send(state)


def keep_draft(state):
    if state["reply"] != FAILED:
        raise ValueError(f"keep_draft from {state['reply']!r}")
    state["reply"] = PENDING
    return state


def set_outage(state, on):
    state["outage"] = on
    return state


def view_model(state):
    """What every surface shows for this mail — the same rule as ``mail_pill``
    and ``reply_strip`` in main.splash: the live reply state outranks the
    static triage tag."""
    pill = {
        SENT: "已回复",
        PENDING: "待发送",
        FAILED: "发送失败",
    }.get(state["reply"])
    strip = ""
    if state["reply"] == PENDING:
        first = state["reply_text"].splitlines()[0] if state["reply_text"] else ""
        strip = f"回复草稿 · 待发送 | {first}".rstrip(" |")
    elif state["reply"] == CONFIRM:
        strip = "确认发送?"
    elif state["reply"] == SENDING:
        strip = "发送中…"
    elif state["reply"] == SENT:
        strip = "已回复 · 刚刚发送,已写入会话"
    elif state["reply"] == FAILED:
        strip = "发送失败 · 邮件服务无响应(练习场景)"
    return {"pill": pill, "strip": strip}


def demo_route():
    """The hackathon demo route: happy path, outage path, recovery path.
    ``scripts/drive-demo.py`` performs this same sequence on the real window
    and captures evidence/ev-01..07."""
    happy = initial_state()
    attach_draft(happy, "确认发布会流程,按当前版本执行。")
    ask_send(happy)
    do_send(happy)
    finish_send(happy)

    outage = initial_state()
    set_outage(outage, True)
    attach_draft(outage, "Q2 终稿确认。")
    ask_send(outage)
    do_send(outage)
    finish_send(outage)          # failed — draft kept
    keep_draft(outage)           # back to pending
    set_outage(outage, False)
    ask_send(outage)
    do_send(outage)
    finish_send(outage)          # retry succeeds
    return {"happy": happy, "outage": outage}
