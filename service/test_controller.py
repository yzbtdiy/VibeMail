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
        c["send_state"] = "sent"
        self.assertEqual(controller.view_model(s, c)["button"], "已随波寄出")
        s["reply"] = "sent"
        self.assertEqual(controller.view_model(s)["pill"], "已回复")
        s["reply"] = "failed"
        self.assertEqual(controller.view_model(s)["pill"], "发送失败")

    def test_demo_route_end_states(self):
        r = controller.demo_route()
        self.assertEqual(r["happy"]["reply"], "sent")
        self.assertEqual(r["outage"]["reply"], "sent")


if __name__ == "__main__":
    unittest.main()
