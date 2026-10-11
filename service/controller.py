"""Compose/send reducer for vibemail 0.7.0.

This module is the verification twin of the state machine implemented in
``bundle/main.splash`` (functions ``open_compose`` / ``set_tone`` /
``do_send`` / ``send_live`` / ``finish_send`` / ``mark_sent`` /
``mark_failed`` / ``retry_send``). The Splash runtime has no unit-test
harness of its own, so the transitions live here as plain Python and are
exercised by ``test_controller.py``; the drive scripts then perform the
same route against the real card-host window. The three must stay in step
— a transition added to the UI belongs here too.

0.7.0 follows the reference design's SINGLE-TAP send (the 0.6.x two-step
confirm is gone): tapping 发送 goes straight to sending, then lands on
sent or failed. A failed send keeps the draft (reply_text never dropped)
and offers retry. State machine:

    ""  --do_send-->  sending --finish-->  sent | failed
    failed --retry_send--> sending (same finish rule)
    failed --keep_draft--> ""            (draft text retained)
    sent is terminal for the mail (已回复 chip)

0.7.28: live sends go through the host's foreground review channel
``mail.review_send`` (``mail.send`` only answers approval_required since
10-04). The review callback settles after physical approval or dismissal:

    sending --finish_review-->  sent | failed | cancelled
    cancelled --retry_send--> sending (review dismissed, nothing was sent;
                                 the mail keeps no failure mark)

0.8.0 adds the Windows-runnable execution loop — host-side drafts via
``mail.compose`` with a ``mail.compose_status`` receipt check:

    "" --do_draft--> composing --finish_draft--> drafted | draft_failed
    draft_failed --do_draft--> composing (text retained, retry)
    drafted counts as host-verified only after verify_draft succeeds;
    a failed receipt check still means the save landed (copy says so)

plus two local-only transitions that mirror the UI: batch vibe sweeps
(archive every visible mail of one vibe, undo restores exactly the swept
set) and schedule-proposal validation (a model-extracted event renders only
when every field passes range checks — half-empty events never render).

Per-mail state lives on the mail object (``reply`` / ``reply_text``), the
compose-local state (``send_state``) drives the button face. Nothing here
talks to a real mail service: practice ``send`` is simulated, exactly as
the UI discloses (practice data; live sends go through the mail host
service's native review sheet).
"""

IDLE = "idle"
SENDING = "sending"
SENT = "sent"
FAILED = "failed"
CANCELLED = "cancelled"

VALID_SEND_STATES = (IDLE, SENDING, SENT, FAILED, CANCELLED)
VALID_REPLY_STATES = ("", SENT, FAILED)

# 0.8.0 draft loop
DRAFT_IDLE = ""
DRAFT_COMPOSING = "composing"
DRAFT_DRAFTED = "drafted"
DRAFT_FAILED = "draft_failed"

VALID_DRAFT_STATES = (DRAFT_IDLE, DRAFT_COMPOSING, DRAFT_DRAFTED, DRAFT_FAILED)


def initial_state():
    """One mail's reply state, mirroring a ``mails[i]`` literal in main.splash."""
    return {"reply": "", "reply_text": "", "outage": False}


def attach_draft(state, text):
    """The tone preview / typed draft is what a send will deliver."""
    if not text:
        raise ValueError("empty draft")
    state["reply_text"] = text
    return state


def do_send(state):
    """Single tap on 发送 (0.7.0): straight to sending, no confirm step.
    The mail's reply state is only written on finish; this returns the new
    compose-local state."""
    if state["reply"] not in ("", FAILED):
        raise ValueError(f"do_send from {state['reply']!r}")
    return {"send_state": SENDING}


def finish_send(state, compose):
    """The 0.9 s practice timer (or the mail service reply) lands here."""
    if compose["send_state"] != SENDING:
        raise ValueError(f"finish_send from {compose['send_state']!r}")
    if state["outage"]:
        compose["send_state"] = FAILED
        compose["error"] = "发送失败(练习场景)"
        state["reply"] = FAILED
    else:
        compose["send_state"] = SENT
        compose["error"] = ""
        state["reply"] = SENT
    return compose


def retry_send(state, compose):
    if compose["send_state"] not in (FAILED, CANCELLED):
        raise ValueError(f"retry_send from {compose['send_state']!r}")
    compose["send_state"] = SENDING
    compose["error"] = ""
    return compose


def finish_review(state, compose, reply):
    """The mail.review_send callback lands here (0.7.28).

    ``reply`` mirrors the host answer: ``{"is_ok": bool, "accepted": bool,
    "error": str}``. Success is accepted-only; a dismissed review sheet
    cancels (nothing sent, no failure mark on the mail); every other error
    fails with the same classified copy the UI shows."""
    if compose["send_state"] != SENDING:
        raise ValueError(f"finish_review from {compose['send_state']!r}")
    if reply.get("is_ok") and reply.get("accepted"):
        compose["send_state"] = SENT
        compose["error"] = ""
        state["reply"] = SENT
        return compose
    if not reply.get("is_ok") and "Review cancelled" in reply.get("error", ""):
        compose["send_state"] = CANCELLED
        compose["error"] = "已取消审阅 · 未发送"
        return compose                       # reply stays ""; draft retained
    compose["send_state"] = FAILED
    error = reply.get("error", "")
    if reply.get("is_ok"):
        compose["error"] = "服务未接受"
    elif "unavailable on this platform" in error:
        compose["error"] = "宿主不支持前台审阅发送(仅 macOS/Android)"
    elif "approval_required" in error:
        compose["error"] = "宿主要求前台审阅批准后才会发送"
    else:
        compose["error"] = error
    state["reply"] = FAILED
    return compose


def keep_draft(state, compose):
    """Leaving a failed/cancelled compose keeps the text and the mail's mark
    as it was (failed cleared; cancelled never had one)."""
    if compose["send_state"] not in (FAILED, CANCELLED):
        raise ValueError(f"keep_draft from {compose['send_state']!r}")
    compose["send_state"] = IDLE
    state["reply"] = ""
    return compose


def set_outage(state, on):
    state["outage"] = on
    return state


# ---- 0.8.0: host-verified drafts ---------------------------------------------

def do_draft(compose):
    """Single tap on 存为草稿: straight to composing, the draft text is only
    read — never cleared — by the save attempt."""
    if compose.get("draft_state", DRAFT_IDLE) == DRAFT_COMPOSING:
        raise ValueError("do_draft while composing")
    compose["draft_state"] = DRAFT_COMPOSING
    compose["draft_msg"] = ""
    return compose


def finish_draft_practice(compose):
    """Practice data keeps a local-only draft and says so."""
    if compose["draft_state"] != DRAFT_COMPOSING:
        raise ValueError(f"finish_draft_practice from {compose['draft_state']!r}")
    compose["draft_state"] = DRAFT_DRAFTED
    compose["draft_msg"] = "练习草稿 · 仅保存在本应用"
    return compose


def finish_draft_live(compose, reply):
    """The mail.compose reply lands here. ``reply`` mirrors the host answer:
    ``{"is_ok": bool, "compose_id": str, "revision": int, "error": str}``.
    A save is not claimed host-verified until verify_draft succeeds."""
    if compose["draft_state"] != DRAFT_COMPOSING:
        raise ValueError(f"finish_draft_live from {compose['draft_state']!r}")
    if reply.get("is_ok"):
        compose["draft_state"] = DRAFT_COMPOSING + ":verify"  # awaiting receipt
        compose["compose_id"] = reply.get("compose_id", "")
        compose["revision"] = reply.get("revision", 0)
    else:
        compose["draft_state"] = DRAFT_FAILED
        compose["draft_msg"] = "草稿保存失败:" + reply.get("error", "")
    return compose


def verify_draft(compose, session, reply):
    """The mail.compose_status receipt check. Verified drafts increment the
    session counter shown in 我的; a failed receipt still leaves the save
    itself intact — the copy distinguishes the two honestly."""
    if compose["draft_state"] != DRAFT_COMPOSING + ":verify":
        raise ValueError(f"verify_draft from {compose['draft_state']!r}")
    compose["draft_state"] = DRAFT_DRAFTED
    if reply.get("is_ok"):
        compose["draft_msg"] = "已存入草稿箱 · 宿主核验"
        session["draft_count"] = session.get("draft_count", 0) + 1
        session["draft_last"] = reply.get("at", "")
    else:
        compose["draft_msg"] = "已存草稿 · 状态核验未回:" + reply.get("error", "")
    return compose


# ---- 0.8.0: batch vibe sweep -------------------------------------------------

def sweep_by_vibe(mails, vibe):
    """Archive every visible mail of one vibe; returns the swept index set so
    undo restores exactly those (归档恢复 stays the permanent path)."""
    swept = []
    for i, m in enumerate(mails):
        if m.get("boxed", "") == "" and m.get("vibe") == vibe:
            m["boxed"] = "archive"
            swept.append(i)
    return swept


def undo_sweep(mails, swept):
    for i in swept:
        mails[i]["boxed"] = ""
    return mails


# ---- 0.8.0: schedule proposal validation -------------------------------------

def valid_event(ev):
    """Mirror of the main.splash range checks: a model-extracted event only
    renders when every field validates — guessed or half-empty events never
    reach the card."""
    if not isinstance(ev, dict):
        return False
    if not ev.get("title"):
        return False
    return (ev.get("y", 0) >= 2026
            and 1 <= ev.get("mo", 0) <= 12
            and 1 <= ev.get("d", 0) <= 31
            and 0 <= ev.get("h", -1) <= 23
            and 0 <= ev.get("mi", -1) <= 59)


def ev_stamp(ev, shift=0):
    """DTSTART digits, with the in-card ±1h correction applied (clamped)."""
    h = min(23, max(0, ev["h"] + shift))
    return (f"{ev['y']}{ev['mo']:02d}{ev['d']:02d}"
            f"T{h:02d}{ev['mi']:02d}00")


def view_model(state, compose=None, live=False):
    """What every surface shows for this mail — the same rules as
    ``reply_state_chip`` and ``send_button``/``draft_button`` in main.splash:
    the mail's live reply state outranks everything on list rows; the compose
    button faces follow the compose-local send/draft states. A live compose
    waits on the host review sheet, so sending says 宿主审阅中 (0.7.28)."""
    pill = {SENT: "已回复", FAILED: "发送失败"}.get(state["reply"])
    button = None
    draft = None
    if compose is not None:
        button = {
            IDLE: "发送",
            SENDING: "宿主审阅中…" if live else "发送中…",
            SENT: "已随波寄出",
            FAILED: "发送失败 · 点按重试",
            CANCELLED: "已取消审阅 · 点按重发",
        }[compose["send_state"]]
        draft = {
            DRAFT_IDLE: "存为草稿",
            DRAFT_COMPOSING: "保存中…",
            DRAFT_COMPOSING + ":verify": "保存中…",
            DRAFT_DRAFTED: "已存草稿",
            DRAFT_FAILED: "保存失败 · 重试",
        }[compose.get("draft_state", DRAFT_IDLE)]
    return {"pill": pill, "button": button, "draft": draft}


def demo_route():
    """The demo route: happy path, outage path, retry path. The drive
    scripts perform this same sequence on the real window."""
    happy = initial_state()
    c = {"send_state": IDLE, "error": ""}
    attach_draft(happy, "Mira,太好了,我很想去!")
    c.update(do_send(happy))
    finish_send(happy, c)

    outage = initial_state()
    c2 = {"send_state": IDLE, "error": ""}
    set_outage(outage, True)
    attach_draft(outage, "确认提交,周三前回复。")
    c2.update(do_send(outage))
    finish_send(outage, c2)        # failed — draft kept
    retry_send(outage, c2)
    set_outage(outage, False)
    finish_send(outage, c2)        # retry succeeds
    return {"happy": happy, "outage": outage}
