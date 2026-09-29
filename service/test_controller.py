"""Unit tests for the reply-lifecycle reducer (unittest, same directory as
the source — the aircon example layout). Run:

    python -m unittest discover -s service
"""

import unittest

import controller


class ReplyLifecycleTests(unittest.TestCase):
    def test_happy_path(self):
        s = controller.initial_state()
        controller.attach_draft(s, "确认发布会流程,按当前版本执行。")
        self.assertEqual(s["reply"], "pending")
        controller.ask_send(s)
        self.assertEqual(s["reply"], "confirm")
        controller.do_send(s)
        self.assertEqual(s["reply"], "sending")
        controller.finish_send(s)
        self.assertEqual(s["reply"], "sent")

    def test_send_requires_explicit_confirm(self):
        s = controller.initial_state()
        controller.attach_draft(s, "草稿")
        with self.assertRaises(ValueError):
            controller.do_send(s)          # cannot fire straight from pending

    def test_cancel_returns_to_pending_with_draft_intact(self):
        s = controller.initial_state()
        controller.attach_draft(s, "草稿正文")
        controller.ask_send(s)
        controller.cancel_send(s)
        self.assertEqual((s["reply"], s["reply_text"]), ("pending", "草稿正文"))

    def test_outage_fails_and_keeps_draft(self):
        s = controller.initial_state()
        controller.set_outage(s, True)
        controller.attach_draft(s, "Q2 终稿确认。")
        controller.ask_send(s)
        controller.do_send(s)
        controller.finish_send(s)
        self.assertEqual(s["reply"], "failed")
        self.assertEqual(s["reply_text"], "Q2 终稿确认。")   # never dropped

    def test_retry_while_outage_still_fails(self):
        s = controller.initial_state()
        controller.set_outage(s, True)
        controller.attach_draft(s, "x")
        controller.ask_send(s)
        controller.do_send(s)
        controller.finish_send(s)
        controller.retry_send(s)
        controller.finish_send(s)
        self.assertEqual(s["reply"], "failed")

    def test_keep_draft_then_resend_succeeds(self):
        s = controller.initial_state()
        controller.set_outage(s, True)
        controller.attach_draft(s, "x")
        controller.ask_send(s)
        controller.do_send(s)
        controller.finish_send(s)
        controller.keep_draft(s)
        self.assertEqual(s["reply"], "pending")
        controller.set_outage(s, False)
        controller.ask_send(s)
        controller.do_send(s)
        controller.finish_send(s)
        self.assertEqual(s["reply"], "sent")

    def test_view_model_matches_ui_copy(self):
        s = controller.initial_state()
        self.assertEqual(controller.view_model(s)["pill"], None)   # triage tag shows
        controller.attach_draft(s, "第一行\n第二行")
        self.assertEqual(controller.view_model(s)["pill"], "待发送")
        self.assertIn("第一行", controller.view_model(s)["strip"])
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
