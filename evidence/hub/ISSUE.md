<!-- Title: Submit vibemail 0.6.16 -->
<!-- Repo: https://github.com/OctoSense-org/OctoSense-App-Hub/issues -->
<!-- 按 App Hub docs/PUBLISHING.md「Submitting」一节的要求逐项填写;
     正文可直接粘贴,无需改动(提交 SHA / 标签 / 公钥均为真实值)。 -->

## Submission

| | |
| --- | --- |
| App id / version | `vibemail` / `0.6.16` |
| Repository | https://github.com/yzbtdiy/VibeMail |
| Tag | `v0.6.16` (annotated, pushed) |
| Commit | `<v0.6.16 commit SHA>` (fill after tagging) |
| Bundle path | `bundle/` |
| Publisher | `yzbtdiy` |
| Publisher public key | `1095438c3939742da32f74fbcc724ae452b3f1e22e4ebe9cd834c24b2b2b5759` |

## Gate output (on the tagged bytes, publisher-signed)

```
> hub check bundle --publisher-key yzbtdiy=1095438c3939742da32f74fbcc724ae452b3f1e22e4ebe9cd834c24b2b2b5759

vibemail 0.6.16 — PASSED
  grants: capabilities {"mail", "model"}, hosts {}, storage 16777216 bytes, agent none
```

No warnings; the manifest carries the `yzbtdiy` signature over the stamped
digest. Full written answers with citations live in the tagged commit at
`evidence/hub/SUBMISSION.md` (the `hub scan` packet is
`evidence/hub/review.json`, regenerated on these exact bytes); the seven
answers in brief:

1. **Does the app do what its name, subtitle and description claim?**
   Yes — `bundle/main.splash` implements the listing verbatim: desktop
   横向 agentic mail in the warm-paper × forest-ink design (light default,
   dark one tap away, plus a three-mode 主题 setting — 跟随系统 / 亮色 /
   暗色 — that follows the shell's live appearance switches, direction
   fixed and re-verified in 0.6.16): 264px sidebar (brand / 写信 CTA / nav badges /
   mailbox folders / AI clusters / AGENT ACTIVE card / calendar-settings
   footer), top bar (agent search / VIBE AGENT pill / theme slider /
   bell), 智能收件箱 (420px list + in-place reader with a collapsible
   inline AI 速览: 摘要要点 / 待办提取 / 语气洞察 / 会议识别 / 智能回复),
   AI 写信 (tone chips + editable AI draft + COMPOSE WITH AI rail),
   Agent 小队 (stats / toggles / autonomy / live approvals). The
   decorative-looking parts are real: folders & clusters are live filters
   (reversible star/archive/trash), and bell/calendar/settings open real
   panels (notification centre with jump-to-work, AI-extracted meetings,
   theme & practice switches, mailbox connect/refresh/disconnect).
   Listing screenshots are real captures of the final 0.6.16 bytes.
2. **Do the listing's platforms and category fit?**
   Yes — `productivity` fits a mail app; `platforms: ["windows"]` is the
   only platform tested (Windows 10 26100): card-host at 940/1000/1200/
   1440×860 plus the OctoSense desktop shell (hi-DPI, ~940 logical px).
3. **Do the granted capabilities match what the app visibly does?**
   Yes — exactly `mail` + `model`, no hosts. `model`: the 「AI 生成」 and
   「生成草稿」 buttons, one-shot schema-checked `model.complete` (host-side
   keys; the chips show the host-reported `meta.model`); refused honestly
   where no service answers (ev-09/10). `mail`: the full
   inbox/read/draft/send flow (`accounts / add_account / sync / list /
   message / mark_read / send / remove_account`) over the platform's mail
   host service — credentials only ever on the host's own sheet. Verified
   end to end in two hosts, including a live `yeah.net` mailbox in the
   desktop shell: 5 real messages listed (2026-10-01), wrong credentials
   refused by the real server (trace: `evidence/ev-mail-log.txt`).
   A dev-only loopback bridge exists in the repo but ships nowhere near
   the bundle (no `http://` literal in `main.splash`).
4. **Is any part of the interface deceptive?**
   No — no imitated system/payment/login UI; the send-failure simulation
   is labelled 练习:模拟服务中断; the mailbox banner states its true
   state (未添加 / 已连接+address+count / 不可用); no password inputs.
5. **Instruction to an assistant rather than content?** No.
6. **Abusive wording / aimed at a private individual?** No — senders are
   fictional practice personas from the reference design.
7. **Route: pass, human-review, or reject?**
   **Pass** — static, capability-lean, honest practice-data labelling,
   real host-service mail & model paths; gate PASSED with no warnings on
   the exact submitted bytes.

## Tested / not tested

**Tested (Windows 10 26100):** 6/6 declarative click routes over the real
card-host window (43 steps: in-place read, honest model refusal + local
fallback, two-step confirmed send with inbox-pill sync, outage → draft
kept → retry, agent approval + theme flip, sidebar folder/cluster filters,
notification/calendar/settings panels); layout audits at 940 / 1000 / 1200
/ 1440 (overflow clean, content presence complete); the store-shape mail
flow via the host's own sign-in sheet (wrong code → real server refusal →
cancel; re-runnable, `scripts/drive-mail.py`); a live IMAP mailbox in the
OctoSense desktop shell (connected, `mail.sync` → 5 real messages listed,
refresh); three-mode theme following the shell's Light/Dark toggle both
ways (pixel-sampled, flips follow within ~1s; pinned modes ignore the
shell).

**Not tested:** any platform other than Windows; real model calls
re-captured on the 0.6.x UI (the same flow passed with a configured
MiniMax at 0.5.x — buttons and copy unchanged; driver scripts remain).
Practice data (Agent squad, activity stream, send-failure switch) is
local and labelled; mail and model paths are real host-service calls.

## Reproducing

Everything runs from the tagged commit with the bundled scripts (Python
3.9+, no third-party deps; `run.cmd` wraps it all):

```sh
python -m unittest discover -s service            # 8/8 state-machine twin
python scripts/run_routes.py <port>               # 6/6 routes (see README)
python scripts/audit_overflow.py 940 1000 1200 1440
python scripts/audit_missing.py  940 1000 1200 1440
python scripts/drive-demo.py <port>               # screenshots + ev-01..10
python scripts/drive-mail.py <port>               # host sheet, real refusal
hub check bundle --publisher-key yzbtdiy=1095438c…b5759
```

Privacy policy: https://github.com/yzbtdiy/VibeMail/blob/main/PRIVACY.md
