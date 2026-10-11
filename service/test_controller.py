"""Unit tests for the compose/send reducer (unittest, same directory as the
source — the aircon example layout). Run:

    python -m unittest discover -s service
"""

import unittest

import controller


class ComposeSendTests(unittest.TestCase):
    def compose(self):
        return {"send_state": controller.IDLE, "error": ""}

    def test_happy_path_single_tap(self):
        s = controller.initial_state()
        c = self.compose()
        controller.attach_draft(s, "Mira,太好了,我很想去!")
        c.update(controller.do_send(s))
        self.assertEqual(c["send_state"], "sending")
        controller.finish_send(s, c)
        self.assertEqual((c["send_state"], s["reply"]), ("sent", "sent"))
        self.assertEqual(s["reply_text"], "Mira,太好了,我很想去!")

    def test_do_send_refuses_after_sent(self):
        s = controller.initial_state()
        c = self.compose()
        controller.attach_draft(s, "x")
        c.update(controller.do_send(s))
        controller.finish_send(s, c)
        with self.assertRaises(ValueError):
            controller.do_send(s)          # sent is terminal for the mail

    def test_outage_fails_and_keeps_draft(self):
        s = controller.initial_state()
        c = self.compose()
        controller.set_outage(s, True)
        controller.attach_draft(s, "确认提交,周三前回复。")
        c.update(controller.do_send(s))
        controller.finish_send(s, c)
        self.assertEqual((c["send_state"], s["reply"]), ("failed", "failed"))
        self.assertEqual(s["reply_text"], "确认提交,周三前回复。")   # never dropped

    def test_retry_while_outage_still_fails(self):
        s = controller.initial_state()
        c = self.compose()
        controller.set_outage(s, True)
        controller.attach_draft(s, "x")
        c.update(controller.do_send(s))
        controller.finish_send(s, c)
        controller.retry_send(s, c)
        controller.finish_send(s, c)
        self.assertEqual(s["reply"], "failed")

    def test_retry_after_outage_recovery_succeeds(self):
        s = controller.initial_state()
        c = self.compose()
        controller.set_outage(s, True)
        controller.attach_draft(s, "x")
        c.update(controller.do_send(s))
        controller.finish_send(s, c)
        controller.retry_send(s, c)
        controller.set_outage(s, False)
        controller.finish_send(s, c)
        self.assertEqual((c["send_state"], s["reply"]), ("sent", "sent"))

    def test_keep_draft_clears_mark_retains_text(self):
        s = controller.initial_state()
        c = self.compose()
        controller.set_outage(s, True)
        controller.attach_draft(s, "保留这份草稿")
        c.update(controller.do_send(s))
        controller.finish_send(s, c)
        controller.keep_draft(s, c)
        self.assertEqual((c["send_state"], s["reply"]), ("idle", ""))
        self.assertEqual(s["reply_text"], "保留这份草稿")

    def test_view_model_matches_ui_copy(self):
        s = controller.initial_state()
        c = self.compose()
        self.assertIsNone(controller.view_model(s)["pill"])    # no chip yet
        self.assertEqual(controller.view_model(s, c)["button"], "发送")
        c["send_state"] = "sending"
        self.assertEqual(controller.view_model(s, c)["button"], "发送中…")
        c["send_state"] = "cancelled"
        self.assertEqual(controller.view_model(s, c)["button"], "已取消审阅 · 点按重发")
        c["send_state"] = "sending"
        self.assertEqual(controller.view_model(s, c, live=True)["button"], "宿主审阅中…")
        c["send_state"] = "sent"
        self.assertEqual(controller.view_model(s, c)["button"], "已随波寄出")
        s["reply"] = "sent"
        self.assertEqual(controller.view_model(s)["pill"], "已回复")
        s["reply"] = "failed"
        self.assertEqual(controller.view_model(s)["pill"], "发送失败")

    def test_review_accepted_marks_sent(self):
        s = controller.initial_state()
        c = self.compose()
        controller.attach_draft(s, "确认参加,期待见面。")
        c.update(controller.do_send(s))
        controller.finish_review(s, c, {"is_ok": True, "accepted": True})
        self.assertEqual((c["send_state"], s["reply"]), ("sent", "sent"))

    def test_review_cancelled_keeps_draft_without_failure_mark(self):
        s = controller.initial_state()
        c = self.compose()
        controller.attach_draft(s, "草稿保留")
        c.update(controller.do_send(s))
        controller.finish_review(
            s, c, {"is_ok": False, "accepted": False,
                   "error": "Review cancelled; nothing was sent"})
        self.assertEqual(c["send_state"], "cancelled")
        self.assertEqual(c["error"], "已取消审阅 · 未发送")
        self.assertEqual(s["reply"], "")            # cancelled sent nothing
        self.assertEqual(s["reply_text"], "草稿保留")

    def test_review_resend_after_cancel(self):
        s = controller.initial_state()
        c = self.compose()
        controller.attach_draft(s, "再试一次")
        c.update(controller.do_send(s))
        controller.finish_review(
            s, c, {"is_ok": False, "accepted": False,
                   "error": "Review cancelled; nothing was sent"})
        controller.retry_send(s, c)
        controller.finish_review(s, c, {"is_ok": True, "accepted": True})
        self.assertEqual((c["send_state"], s["reply"]), ("sent", "sent"))

    def test_review_platform_and_approval_errors_classified(self):
        s = controller.initial_state()
        c = self.compose()
        controller.attach_draft(s, "x")
        c.update(controller.do_send(s))
        controller.finish_review(
            s, c, {"is_ok": False, "accepted": False,
                   "error": "Physical Mail send approval is unavailable on this platform"})
        self.assertEqual((c["send_state"], c["error"]),
                         ("failed", "宿主不支持前台审阅发送(仅 macOS/Android)"))
        controller.retry_send(s, c)
        controller.finish_review(
            s, c, {"is_ok": False, "accepted": False,
                   "error": "approval_required: use mail.review_send …"})
        self.assertEqual((c["send_state"], c["error"]),
                         ("failed", "宿主要求前台审阅批准后才会发送"))

    def test_review_unaccepted_ok_answer_fails_honestly(self):
        s = controller.initial_state()
        c = self.compose()
        controller.attach_draft(s, "x")
        c.update(controller.do_send(s))
        controller.finish_review(s, c, {"is_ok": True, "accepted": False})
        self.assertEqual((c["send_state"], c["error"], s["reply"]),
                         ("failed", "服务未接受", "failed"))

    def test_demo_route_end_states(self):
        r = controller.demo_route()
        self.assertEqual(r["happy"]["reply"], "sent")
        self.assertEqual(r["outage"]["reply"], "sent")


class DraftLoopTests(unittest.TestCase):
    """0.8.0: mail.compose + mail.compose_status host-verified drafts."""

    def compose(self):
        return {"send_state": controller.IDLE, "error": ""}

    def test_practice_draft_is_local_and_labelled(self):
        c = self.compose()
        controller.do_draft(c)
        self.assertEqual(c["draft_state"], "composing")
        controller.finish_draft_practice(c)
        self.assertEqual(c["draft_state"], "drafted")
        self.assertEqual(c["draft_msg"], "练习草稿 · 仅保存在本应用")

    def test_live_draft_verified_counts_session(self):
        c = self.compose()
        session = {}
        controller.do_draft(c)
        controller.finish_draft_live(
            c, {"is_ok": True, "compose_id": "c-1", "revision": 1})
        self.assertEqual(c["compose_id"], "c-1")
        controller.verify_draft(c, session, {"is_ok": True, "at": "14:32"})
        self.assertEqual(c["draft_state"], "drafted")
        self.assertEqual(c["draft_msg"], "已存入草稿箱 · 宿主核验")
        self.assertEqual(session["draft_count"], 1)
        self.assertEqual(session["draft_last"], "14:32")

    def test_live_draft_unverified_receipt_still_saved(self):
        c = self.compose()
        session = {}
        controller.do_draft(c)
        controller.finish_draft_live(
            c, {"is_ok": True, "compose_id": "c-2", "revision": 1})
        controller.verify_draft(c, session, {"is_ok": False, "error": "timeout"})
        self.assertEqual(c["draft_state"], "drafted")
        self.assertIn("核验未回", c["draft_msg"])
        self.assertEqual(session.get("draft_count", 0), 0)   # not verified

    def test_live_draft_compose_error_fails_and_retries(self):
        c = self.compose()
        controller.do_draft(c)
        controller.finish_draft_live(c, {"is_ok": False, "error": "resource_limit"})
        self.assertEqual(c["draft_state"], "draft_failed")
        self.assertIn("resource_limit", c["draft_msg"])
        controller.do_draft(c)                                # retry
        controller.finish_draft_live(
            c, {"is_ok": True, "compose_id": "c-3", "revision": 1})
        controller.verify_draft(c, {}, {"is_ok": True, "at": "15:01"})
        self.assertEqual(c["draft_state"], "drafted")

    def test_draft_button_faces(self):
        c = self.compose()
        s = controller.initial_state()
        self.assertEqual(controller.view_model(s, c)["draft"], "存为草稿")
        controller.do_draft(c)
        self.assertEqual(controller.view_model(s, c)["draft"], "保存中…")
        controller.finish_draft_practice(c)
        self.assertEqual(controller.view_model(s, c)["draft"], "已存草稿")
        controller.do_draft(c)
        controller.finish_draft_live(c, {"is_ok": False, "error": "x"})
        self.assertEqual(controller.view_model(s, c)["draft"], "保存失败 · 重试")


class SweepTests(unittest.TestCase):
    """0.8.0: batch vibe sweep with exact undo."""

    def mails(self):
        return [{"vibe": v, "boxed": ""} for v in
                ("calm", "focus", "calm", "joy", "calm")]

    def test_sweep_archives_only_matching_visible(self):
        ms = self.mails()
        ms[1]["boxed"] = "archive"          # already archived: untouched
        swept = controller.sweep_by_vibe(ms, "calm")
        self.assertEqual(swept, [0, 2, 4])
        self.assertEqual([m["boxed"] for m in ms],
                         ["archive", "archive", "archive", "", "archive"])

    def test_undo_restores_exactly_the_swept_set(self):
        ms = self.mails()
        swept = controller.sweep_by_vibe(ms, "calm")
        controller.undo_sweep(ms, swept)
        self.assertEqual([m["boxed"] for m in ms], ["", "", "", "", ""])

    def test_sweep_empty_vibe_is_noop(self):
        ms = self.mails()
        self.assertEqual(controller.sweep_by_vibe(ms, "spark"), [])


class EventValidationTests(unittest.TestCase):
    """0.8.0: schedule proposals render only when every field validates."""

    GOOD = {"title": "与 Mira 的海边周末", "label": "周六 10/17",
            "place": "海边玻璃小屋", "y": 2026, "mo": 10, "d": 17, "h": 9, "mi": 20}

    def test_good_event_passes(self):
        self.assertTrue(controller.valid_event(self.GOOD))

    def test_empty_title_never_renders(self):
        ev = dict(self.GOOD, title="")
        self.assertFalse(controller.valid_event(ev))

    def test_out_of_range_fields_never_render(self):
        for bad in (dict(self.GOOD, y=1999), dict(self.GOOD, mo=13),
                    dict(self.GOOD, d=0), dict(self.GOOD, h=24),
                    dict(self.GOOD, mi=-1)):
            self.assertFalse(controller.valid_event(bad))

    def test_stamp_zero_pads_and_shifts(self):
        self.assertEqual(controller.ev_stamp(self.GOOD), "20261017T092000")
        self.assertEqual(controller.ev_stamp(self.GOOD, shift=1), "20261017T102000")
        self.assertEqual(controller.ev_stamp(self.GOOD, shift=-20), "20261017T002000")


if __name__ == "__main__":
    unittest.main()
