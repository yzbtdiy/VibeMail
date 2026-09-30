"""vibemail bridge: IMAP/SMTP <-> plain HTTP JSON on 127.0.0.1.

Why this exists: a contained OctoSense app cannot speak IMAP/SMTP itself
(no raw sockets for policed heaps, and it must never hold mail credentials).
This bridge runs on YOUR machine, holds the account's authorization code in
config.json (never in the app), and exposes a small JSON API whose shape
follows the platform's own mail host service (mail.list / mail.message /
mail.send), so the app can later switch to the official service unchanged.

Only loopback, plain HTTP: the app's network layer allows cleartext to
loopback only, so no certificate is needed and nothing is exposed off-device.

Run:  python bridge.py            (reads config.json beside this file)
Test: python -m unittest discover -s bridge
"""

import email
import email.header
import email.utils
import html
import imaplib
import json
import re
import smtplib
import threading
from email.mime.text import MIMEText
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

CONFIG_PATH = Path(__file__).resolve().parent / "config.json"
LISTEN_HOST = "127.0.0.1"
LISTEN_PORT = 8443
PREVIEW_CHARS = 60

# ---------------------------------------------------------------- parsing

def decode_header_value(raw):
    """Decode an RFC2047 header ('=?utf-8?b?...?=' etc.) to text."""
    if raw is None:
        return ""
    parts = []
    for chunk, charset in email.header.decode_header(raw):
        if isinstance(chunk, bytes):
            parts.append(chunk.decode(charset or "utf-8", errors="replace"))
        else:
            parts.append(chunk)
    return "".join(parts).strip()


def html_to_text(html_text):
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", html_text)
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</p>", "\n", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"[ \t]+", " ", text)


def extract_body(msg):
    """Prefer text/plain; fall back to a textified text/html part."""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and not part.get_filename():
                return part.get_payload(decode=True).decode(
                    part.get_content_charset() or "utf-8", errors="replace")
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                return html_to_text(part.get_payload(decode=True).decode(
                    part.get_content_charset() or "utf-8", errors="replace"))
        return ""
    payload = msg.get_payload(decode=True)
    if payload is None:
        return ""
    text = payload.decode(msg.get_content_charset() or "utf-8", errors="replace")
    if msg.get_content_type() == "text/html":
        return html_to_text(text)
    return text


def parse_message(raw_bytes, uid):
    msg = email.message_from_bytes(raw_bytes)
    sender_full = decode_header_value(msg.get("From", ""))
    name, addr = email.utils.parseaddr(sender_full)
    subject = decode_header_value(msg.get("Subject", ""))
    date_hdr = msg.get("Date", "")
    try:
        dt = email.utils.parsedate_to_datetime(date_hdr)
        time_str = dt.strftime("%m-%d %H:%M")
    except Exception:
        time_str = date_hdr
    body = extract_body(msg).strip()
    preview = re.sub(r"\s+", " ", body)[:PREVIEW_CHARS]
    return {
        "id": str(uid),
        "sender": name or addr,
        "address": addr,
        "subject": subject or "(no subject)",
        "preview": preview,
        "time": time_str,
        "date": date_hdr,
        "body": body,
        "unread": False,          # filled by the caller from IMAP flags
    }


# ---------------------------------------------------------------- mail account

class MailAccount:
    """One IMAP+SMTP account. Serialized by a lock: imaplib is not shared."""

    def __init__(self, cfg):
        self.cfg = cfg
        self.lock = threading.Lock()

    @property
    def email(self):
        return self.cfg["email"]

    def _imap(self):
        ic = self.cfg["imap"]
        cls = imaplib.IMAP4_SSL if ic.get("ssl", True) else imaplib.IMAP4
        m = cls(ic["host"], ic["port"])
        m.login(self.cfg["email"], self.cfg["auth_code"])
        return m

    def check(self):
        with self.lock:
            m = self._imap()
            try:
                status, _ = m.select("INBOX", readonly=True)
                return status == "OK"
            finally:
                m.logout()

    def list(self, limit=20):
        with self.lock:
            m = self._imap()
            try:
                status, data = m.select("INBOX", readonly=True)
                if status != "OK":
                    raise RuntimeError("cannot select INBOX")
                total = int(data[0])
                status, uids = m.uid("search", None, "ALL")
                if status != "OK":
                    raise RuntimeError("uid search failed")
                uid_list = uids[0].split()
                newest_first = list(reversed(uid_list))[:limit]
                messages = []
                for uid in newest_first:
                    status, fetched = m.uid("fetch", uid, "(FLAGS RFC822)")
                    if status != "OK" or not fetched or fetched[0] is None:
                        continue
                    flags = b""
                    raw = b""
                    for item in fetched:
                        if isinstance(item, tuple):
                            meta, raw = item[0], item[1]
                            flags = meta or b""
                    parsed = parse_message(raw, uid)
                    parsed["unread"] = b"\\Seen" not in flags
                    messages.append(parsed)
                return {"total": total, "messages": messages}
            finally:
                m.logout()

    def message(self, uid):
        with self.lock:
            m = self._imap()
            try:
                m.select("INBOX", readonly=True)
                status, fetched = m.uid("fetch", uid, "(RFC822)")
                if status != "OK" or not fetched or fetched[0] is None:
                    raise RuntimeError(f"no message uid={uid}")
                raw = next(item[1] for item in fetched if isinstance(item, tuple))
                return parse_message(raw, uid)
            finally:
                m.logout()

    def mark_read(self, uid):
        with self.lock:
            m = self._imap()
            try:
                m.select("INBOX")
                m.uid("store", uid, "+FLAGS", "(\\Seen)")
                return True
            finally:
                m.logout()

    def send(self, to, subject, body):
        with self.lock:
            sc = self.cfg["smtp"]
            cls = smtplib.SMTP_SSL if sc.get("ssl", True) else smtplib.SMTP
            s = cls(sc["host"], sc["port"])
            try:
                s.login(self.cfg["email"], self.cfg["auth_code"])
                msg = MIMEText(body, "plain", "utf-8")
                msg["Subject"] = subject
                msg["From"] = self.cfg["email"]
                msg["To"] = to
                s.send_message(msg)
                return {"accepted": True}
            finally:
                s.quit()


# ---------------------------------------------------------------- HTTP server

def make_handler(account):
    class Handler(BaseHTTPRequestHandler):
        server_version = "vibemail-bridge/1.0"

        def _json(self, code, obj):
            body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _account_or_error(self):
            if account is None:
                self._json(503, {"ok": False, "error": "bridge online, mailbox not configured"})
                return None
            return True

        def do_GET(self):
            url = urlparse(self.path)
            if url.path == "/health":
                if account is None:
                    self._json(200, {"ready": False, "error": "mailbox not configured"})
                    return
                try:
                    account.check()
                    self._json(200, {"ready": True, "email": account.email})
                except Exception as e:
                    self._json(200, {"ready": False, "error": f"mailbox login failed: {e}"})
                return
            if url.path == "/list":
                if not self._account_or_error():
                    return
                try:
                    limit = int(parse_qs(url.query).get("limit", ["20"])[0])
                    self._json(200, account.list(limit=limit))
                except Exception as e:
                    self._json(502, {"error": f"imap: {e}"})
                return
            if url.path == "/message":
                if not self._account_or_error():
                    return
                try:
                    uid = parse_qs(url.query)["id"][0]
                    self._json(200, account.message(uid))
                except Exception as e:
                    self._json(502, {"error": f"imap: {e}"})
                return
            self._json(404, {"error": "not found"})

        def do_POST(self):
            url = urlparse(self.path)
            if url.path == "/send":
                if not self._account_or_error():
                    return
                try:
                    data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                    self._json(200, account.send(data["to"], data["subject"], data["body"]))
                except Exception as e:
                    self._json(502, {"error": f"smtp: {e}"})
                return
            if url.path == "/mark_read":
                if not self._account_or_error():
                    return
                try:
                    data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                    account.mark_read(data["id"])
                    self._json(200, {"ok": True})
                except Exception as e:
                    self._json(502, {"error": f"imap: {e}"})
                return
            self._json(404, {"error": "not found"})

        def log_message(self, fmt, *args):
            print("bridge:", fmt % args)

    return Handler


def load_account():
    if not CONFIG_PATH.exists():
        return None
    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    if not cfg.get("auth_code"):
        return None
    return MailAccount(cfg)


def main():
    account = load_account()
    state = "mailbox configured" if account else "NO mailbox (copy config.example.json -> config.json)"
    srv = ThreadingHTTPServer((LISTEN_HOST, LISTEN_PORT), make_handler(account))
    print(f"vibemail bridge on http://{LISTEN_HOST}:{LISTEN_PORT} — {state}")
    srv.serve_forever()


if __name__ == "__main__":
    main()
