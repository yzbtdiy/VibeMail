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

Per-mail state lives on the mail object (``reply`` / ``reply_text``), the
compose-local state (``send_state``) drives the button face. Nothing here
talks to a real mail service: ``send`` is simulated, exactly as the UI
discloses (practice data; live sends go through the mail host service).
"""

IDLE = "idle"
SENDING = "sending"
SENT = "sent"
FAILED = "failed"

VALID_SEND_STATES = (IDLE, SENDING, SENT, FAILED)
VALID_REPLY_STATES = ("", SENT, FAILED)


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
    if compose["send_state"] != FAILED:
        raise ValueError(f"retry_send from {compose['send_state']!r}")
    compose["send_state"] = SENDING
    compose["error"] = ""
    return compose


def keep_draft(state, compose):
    """Leaving a failed compose keeps the text and clears the mail's mark."""
    if compose["send_state"] != FAILED:
        raise ValueError(f"keep_draft from {compose['send_state']!r}")
    compose["send_state"] = IDLE
    state["reply"] = ""
    return compose


def set_outage(state, on):
    state["outage"] = on
    return state


def view_model(state, compose=None):
    """What every surface shows for this mail — the same rules as
    ``reply_state_chip`` and ``send_button`` in main.splash: the mail's
    live reply state outranks everything on list rows; the compose button
    face follows the compose-local send state."""
    pill = {SENT: "已回复", FAILED: "发送失败"}.get(state["reply"])
    button = None
    if compose is not None:
        button = {
            IDLE: "发送",
            SENDING: "发送中…",
            SENT: "已随波寄出",
            FAILED: "发送失败 · 点按重试",
        }[compose["send_state"]]
    return {"pill": pill, "button": button}


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
