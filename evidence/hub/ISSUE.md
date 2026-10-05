<!-- Title: Submit vibemail 0.7.25 -->
<!-- Repo: https://github.com/OctoSense-org/OctoSense-App-Hub/issues -->
<!-- 按 App Hub docs/PUBLISHING.md「Submitting」一节的要求逐项填写;
     正文可直接粘贴,无需改动(提交 SHA 开 issue 时回填,其余均为真实值)。 -->

## Submission

| | |
| --- | --- |
| App id / version | `vibemail` / `0.7.25` |
| Repository | https://github.com/yzbtdiy/VibeMail |
| Tag | `v0.7.25` (annotated, pushed) |
| Commit | `<v0.7.25 commit SHA>` (fill after tagging) |
| Bundle path | `bundle/` |
| Publisher | `yzbtdiy` |
| Publisher public key | `1095438c3939742da32f74fbcc724ae452b3f1e22e4ebe9cd834c24b2b2b5759` |

## Gate output (on the tagged bytes, publisher-signed)

```
> hub check bundle --publisher-key yzbtdiy=1095438c3939742da32f74fbcc724ae452b3f1e22e4ebe9cd834c24b2b2b5759

vibemail 0.7.25 — PASSED
  grants: capabilities {"mail", "model", "storage"}, hosts {}, storage 4194304 bytes, agent none
```

No warnings; the manifest carries the `yzbtdiy` signature over the stamped
digest. Full written answers with citations live in the tagged commit at
`evidence/hub/SUBMISSION.md` (the `hub scan` packet is
`evidence/hub/review.json`, regenerated on these exact bytes); the seven
answers in brief:

1. **Does the app do what its name, subtitle and description claim?**
   Yes — `bundle/main.splash` implements the listing verbatim: a
   width-adaptive phone-column app (native 412px, fills any window) in the
   warm-paper × charcoal design with five invariant vibe colours. Five
   screens: 收件箱 (time greeting, live unread count, AI 心情播报 line
   labelled 模型生成/生成中…/固定文案, vibe filter chips that really filter,
   aura cards with unread dot/star/importance), 星轨 Orbit (bubbles,
   size=importance, colour=vibe, sin/cos drift, tap opens), 详情 Detail
   (vibe chip, AI 三行摘要 with honest source labels — 练习摘要/模型生成/
   生成中/服务不可用/正文截取, full body, 星标/归档/回复), 写信 Compose
   (五档语气滑杆 真诚随意↔轻松幽默↔自然友好↔简洁专业↔正式得体 real-time
   rewrite; single-tap send: 发送中…→已随波寄出 / 失败保留草稿可重试),
   我的 Settings (theme quick-toggle + 跟随系统/亮色/暗色 following the
   shell live, capability-declaration card, mailbox connect via the host's
   own sheet / refresh / two-step disconnect / archive restore, labelled
   practice outage switch). Floating glass nav pill with a tap-guard.
   Listing screenshots are real captures of the final UI (2026-10-04).
2. **Do the listing's platforms and category fit?**
   Yes — `productivity` fits a mail app; `platforms: ["windows"]` is the
   only platform tested (Windows 10 26100): card-host at 412/700/1200×860
   plus the OctoSense desktop shell. No other platform is claimed.
3. **Do the granted capabilities match what the app visibly does?**
   Yes — exactly `mail` + `model` + `storage`, no network hosts.
   `mail`: the full inbox/read/send flow (`accounts / add_account / sync /
   list / message / mark_read / send / remove_account`) over the platform's
   mail host service — credentials only ever on the host's own sheet,
   host-side vault. Verified in the desktop shell with a real mailbox:
   real INBOX listed and keyword-classified, first-open AI summaries on
   real mail (ev-20/21); wrong credentials refused by the real server
   (trace: `evidence/ev-mail-log.txt`; sheet flow ev-13..16).
   `model`: AI 三行摘要 / tone rewrite / 心情播报, one-shot schema-checked
   `model.complete`; 0.7.25 request discipline — one call per open, 30 s
   patience, no resend loop (the earlier loop could burn the host's per-app
   daily budget); rate/budget refusals shown with the host's wording
   (「限速·重开重试」「今日额度用完」); honest fallbacks (正文截取/练习
   摘要/固定文案) where no service answers. `storage`: `theme.json` in the
   4 MiB sandbox. A dev-only loopback bridge exists in the repo but ships
   nowhere near the bundle (no `http://` literal in `main.splash`).
4. **Is any part of the interface deceptive?**
   No — no imitated system/payment/login UI and no credential typed in the
   app; the send-failure simulation is labelled 练习 and togglable; AI
   features carry provenance lines; the mailbox banner states its true
   state (未添加 / 已连接+address+count / 不可用 / 同步中).
5. **Instruction to an assistant rather than content?** No.
6. **Abusive wording / aimed at a private individual?** No — practice
   senders are fictional personas from the reference design; live mail is
   rendered as received.
7. **Route: pass, human-review, or reject?**
   **Pass** — static, capability-lean, honest practice-data labelling,
   real host-service mail & model paths; gate PASSED with no warnings on
   the exact submitted bytes.

## Tested / not tested

**Tested (Windows 10 26100):** 6/6 declarative click routes over the real
card-host window (42 steps: vibe filter + detail summary, orbit bubble open
+ tri-state theme, five-stop tone rewrite, single-tap send + replied chip,
outage → draft kept → retry, archive/restore; the runner exits 0 only on a
full pass), 2026-10-04; layout audits at 412 / 700 / 1200
(overflow clean, content presence complete); 8/8 state-machine unit tests;
the store-shape mail flow via the host's own sign-in sheet (wrong code →
real server refusal → cancel; `scripts/drive-mail.py`); a live IMAP
mailbox in the OctoSense desktop shell with real model output on first
open (ev-20/21; a full validation round consumed 5 model calls — the
0.7.25 one-call-per-open discipline); three-mode theme following the
shell's appearance toggle both ways (~1-2 s, pixel-sampled).

**Not tested:** any platform other than Windows; the card-host store-shape
mail flow re-run on the exact 0.7.25 bytes (last recorded run 2026-10-02,
re-runnable; the shell live-mail path re-verified 2026-10-04 exercises the
same mail methods end to end). Practice data (eight practice mails, five
tone variants each, send-failure switch) is local and labelled; mail and
model paths are real host-service calls.

## Reproducing

Everything runs from the tagged commit with the bundled scripts (Python
3.9+, no third-party deps; `run.cmd` wraps it all):

```sh
python -m unittest discover -s service            # 8/8 state-machine twin
python scripts/run_routes.py <port>               # 6/6 routes (see README)
python scripts/audit_overflow.py 412 700 1200
python scripts/audit_missing.py  412 700 1200
python scripts/drive-demo.py <port>               # screenshots + ev-01..10
python scripts/drive-mail.py <port>               # host sheet, real refusal
run.cmd shell                                     # live mail + model in the shell
hub check bundle --publisher-key yzbtdiy=1095438c…b5759
```

Privacy policy: https://github.com/yzbtdiy/VibeMail/blob/main/PRIVACY.md
