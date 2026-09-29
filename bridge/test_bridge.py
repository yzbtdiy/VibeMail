"""Unit tests for the bridge's pure parsing layer (no network, no account).

Run:  python -m unittest discover -s bridge
"""

import email
import unittest
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formatdate

import bridge


def build_message(subject, sender, body, charset="utf-8"):
    msg = MIMEText(body, "plain", charset)
    msg["Subject"] = Header(subject, charset)
    msg["From"] = sender
    msg["Date"] = formatdate()
    return msg.as_bytes()


class ParsingTests(unittest.TestCase):
    def test_plain_ascii(self):
        raw = build_message("Release plan", "Zhang Wei <zhang@example.com>", "Please confirm.")
        parsed = bridge.parse_message(raw, 42)
        self.assertEqual(parsed["id"], "42")
        self.assertEqual(parsed["sender"], "Zhang Wei")
        self.assertEqual(parsed["address"], "zhang@example.com")
        self.assertEqual(parsed["subject"], "Release plan")
        self.assertIn("Please confirm.", parsed["body"])
        self.assertIn("Please confirm.", parsed["preview"])

    def test_chinese_subject_and_body(self):
        raw = build_message("产品发布会流程确认", "张伟 <zhang@example.com>",
                            "小林:\n\n请确认发布会流程。")
        parsed = bridge.parse_message(raw, 7)
        self.assertEqual(parsed["subject"], "产品发布会流程确认")
        self.assertEqual(parsed["sender"], "张伟")
        self.assertIn("请确认发布会流程", parsed["body"])

    def test_preview_collapses_whitespace_and_truncates(self):
        body = "第一段\n\n\n   多余空白\t制表  " + "长" * 100
        raw = build_message("s", "a <a@example.com>", body)
        parsed = bridge.parse_message(raw, 1)
        self.assertLessEqual(len(parsed["preview"]), bridge.PREVIEW_CHARS)
        self.assertNotIn("\n", parsed["preview"])

    def test_html_fallback_to_text(self):
        msg = MIMEText("<p>你好<br/>世界</p><script>x()</script>", "html", "utf-8")
        msg["Subject"] = "html"
        msg["From"] = "a <a@example.com>"
        msg["Date"] = formatdate()
        text = bridge.extract_body(email.message_from_bytes(msg.as_bytes()))
        self.assertIn("你好", text)
        self.assertIn("世界", text)
        self.assertNotIn("script", text)
        self.assertNotIn("<", text)

    def test_decode_header_plain_string(self):
        self.assertEqual(bridge.decode_header_value("plain"), "plain")
        self.assertEqual(bridge.decode_header_value(None), "")


if __name__ == "__main__":
    unittest.main()
