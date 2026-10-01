#!/usr/bin/env python3
"""Read-only mailbox probe: ask the REAL IMAP server what it sees.

usage:  python scripts/mailbox_probe.py 你 的授权码
(optional env override: MAIL_USER, default yzbtdiy@yeah.net)

Only touches imap.yeah.net with your own credentials; prints:
  1. every folder on the server with its message count
  2. the newest INBOX subjects
Nothing is modified (no mark-read, no delete).
"""
import imaplib
import os
import sys

USER = os.environ.get("MAIL_USER", "yzbtdiy@yeah.net")
HOST = "imap.yeah.net"

if len(sys.argv) < 2:
    sys.exit("usage: python scripts/mailbox_probe.py <授权码>")

m = imaplib.IMAP4_SSL(HOST, 993)
m.login(USER, sys.argv[1])
print(f"登录成功: {USER}@{HOST}")

typ, data = m.list()
print("\n== 服务器上的文件夹 ==")
folders = []
for line in data or []:
    raw = line.decode("utf-8", "replace") if isinstance(line, bytes) else str(line)
    name = raw.rsplit('"', 2)[-2] if '"' in raw else raw
    folders.append(name)

for name in folders:
    try:
        st, d = m.select(name, readonly=True)
        if st == "OK":
            print(f"  {d[0].decode():>6s} 封  {name}")
    except Exception as e:
        print(f"  跳过 {name}: {e}")

print("\n== INBOX 最新 5 封主题 ==")
m.select("INBOX", readonly=True)
typ, d = m.search(None, "ALL")
ids = d[0].split()
print(f"INBOX 共 {len(ids)} 封")
for i in ids[-5:][::-1]:
    typ, dd = m.fetch(i, "(BODY.PEEK[HEADER.FIELDS (SUBJECT FROM DATE)])")
    for part in dd:
        if isinstance(part, tuple):
            print("  " + part[1].decode("utf-8", "replace").strip().replace("\r\n", " | ")[:110])

m.logout()
