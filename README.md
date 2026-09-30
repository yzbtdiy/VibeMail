# VibeMail (vibemail)

English | [简体中文](README.zh-CN.md)

A concept app for the Agentic App Hackathon 2026 (mail scene). 0.5.4 surfaces the ACTUAL model the host used — the model chip next to 生成草稿 and the summary pill read meta.model from the model.complete reply (a small host-side addition), so once a call succeeds the fictional GPT-Vibe 4 placeholder is replaced by the real configured model's name. 0.5.3 de-nests the compose inputs (prompt + AI draft render as a single box each, text on the card, like the web); 0.5.2 turns the theme pill and sidebar footer buttons into native-widget ICONS (sun/moon/calendar/sliders — no text glyphs); 0.5.1 refined the 0.5.0 full UI REBUILD: the three inbox panes (list | reader | AI Copilot) now scroll INDEPENDENTLY — like the web design — instead of one page scroll, and nothing shows below shorter panes. 0.5.0 was a FULL UI REBUILD from the latest design (`bundle/main.splash`): the forest-ink × warm-paper dual theme (deep forest dark by default, warm sand light — flipped from the top-bar pill), a sidebar (写信·AI 起草 / 收件箱 / Agent 小队 nav, mailbox folders, AI clusters, AGENT ACTIVE mini card), a top bar (agent-ask search, agent pill, theme toggle), a THREE-PANE inbox (mail list | in-place reader | AI Copilot with 摘要 / 待办提取 / 语气洞察 / 智能回复), a compose card with a COMPOSE WITH AI rail, and the agent squad panel (stats, toggles, autonomy, live activity stream). Clicking a card opens the mail IN PLACE — no screen push. Audited at 1200 and 1440 (run.cmd default 1200x860). AI summary and drafting verified against a REAL configured provider (MiniMax via the OctoSense shell) — ev-22/ev-23.

**Capabilities & data**: the app requests `model` and `mail`.
`mail`: real IMAP/SMTP goes through the platform's mail host service —
accounts are added on the host's own sign-in sheet and the authorization
code stays in the host's vault, never in the app. Verified in **two**
hosts. (1) The real **OctoSense desktop shell** (strongest, ev-17..19):
the bundle — same id, same bytes — is admitted through a local signed
hub catalog (`../octosense-local-hub/`, anchor via `OCTOSENSE_HUB_ANCHOR`,
install via `OCTOSENSE_APP_DATA`), launches as a window-manager client,
and the shell's own Mail service does the work: the official
「OctoSense · Add a mail account」 sheet appears, and a wrong password is
rejected by the real `imap.qq.com`. (2) A local `card-host` build that
registers a reference mail service (`OctoSense-App-Hub/crates/mail-service`,
the documented shell-extension path) — ev-13..16: 添加账号 opens the
host sheet, a wrong code is rejected by the real `imap.qq.com` (verbatim
server text), 取消 answers the app's add_account with an error. Where no
service is registered (a stock card-host), the banner says so and
labelled practice data is used. `model`: AI summary and drafting go
through the one-shot model service (schema-checked, daily per-app
budget) using the model the person configured; keys never reach the app;
fallbacks are labelled. The Agent squad and activity stream are practice
data (no-facts rule).

## Layout

```text
source/        design sources: the web reference the UI was rebuilt from,
               design-brief.md (palette, view specs, responsive rules)
service/       reply-lifecycle reducer (controller.py — the verification twin of
               the main.splash state machine) + unittest (8 cases)
bridge/        DEV-ONLY, now optional: an IMAP/SMTP <-> loopback HTTP bridge
               (credentials live only in bridge/config.json, gitignored;
               5 parsing unit tests). Superseded by the platform route below.
dev/           DEV-ONLY: the bridge adapter that scripts/dev_bundle.py splices
               over the MARKER:ADAPTER block (never part of the submission)
scripts/       run_app.py — the engine behind run.cmd (launch, demo, mail,
               shell, check);
               drive-demo.py — drives the real card-host window over the
               Makepad remote bridge through the full demo task (two widths
               for the responsive claims);
               drive-mail.py — drives the shipped bundle through the
               platform mail service in card-host (no-account → host
               sheet → real rejection → cancel);
               official_sheet_run.py — the same flow inside the real
               OctoSense desktop shell (the official sheet, the
               official service's real imap.qq.com rejection);
               ai_test.py — the AI summary/draft driver inside the shell
               (ev-22..24); audit_missing/audit_overflow — width audits;
               dev_bundle.py — assembles build/dev-bundle (dev-only)
evidence/      run evidence: ev-01..08.png (reply lifecycle, agents approval),
               ev-09/10 (model unavailable), ev-13..16 (store-form mail in
               card-host), ev-17..19 (the same bundle inside the OctoSense
               desktop shell: running, official sheet, official service's
               real IMAP rejection), ev-20 (desktop master-detail),
               ev-21 (light theme), ev-22..24 (real AI summary/draft in
               the shell, model chip), final-snap.json, final-log.txt,
               hub/ (scan packet + SUBMISSION.md answers)
bundle/        THE SUBMISSION — main.splash, assets/icon.svg, listing.json,
               manifest.json, screenshots/01..05 (hub check PASSED)
```

## Demo task (maps to the judging criteria)

识别 (AI triage banner + priority meters + summary card with points,
suggested actions, meeting detection, sentiment) → 提议 (editable AI draft,
explicit recipient, tone chips, one-tap smart replies) → 授权 (two-step
confirmed send) → 结果核验 (sent strip in the read view, synced pill in the
inbox) → 失败处理 (practice outage switch: send fails, draft kept, retry
succeeds) → 真实模型调用 (ev-09/ev-10: card-host honestly answers
`no service answers "model"` and the UI says so; the same button produces
real model output in an OctoSense desktop Shell built from main ≥ 2026-09-28
with AI providers configured).

## Reproduce (Windows 10 26100 — the only platform tested)

Build the host with the mail service once (this repo's local hub checkout;
`register()` is already wired into `crates/card-host/src/host.rs`):

```sh
cd ../OctoSense-App-Hub && cargo build --release -p octosense-card-host
# the build lands in %CARGO_TARGET_DIR% (D:\Users\yzbtdiy\Cache\CARGO_TARGET)
```

Then run the shipped bundle in it (both widths exercise the responsive
layouts; the driver parks the real mouse cursor away from the driven
window — OS cursor events otherwise eat the synthetic taps):

```sh
python -m unittest discover -s service
set MAKEPAD_REMOTE=8146
start "" D:\Users\yzbtdiy\Cache\CARGO_TARGET\release\card-host.exe --bundle bundle ^
    --app-data .local-state --allow-unsigned --stamp --size 412x860
python scripts/drive-demo.py 8146      # full lifecycle + model-unavailable states
python scripts/drive-mail.py 8146      # store-form mail: sheet, real rejection, cancel
rem desktop width: relaunch with --size 1200x860 and click any mail —
rem the inbox becomes list+placeholder, the read view a master-detail (ev-20)
../OctoSense-App-Hub/target/release/hub.exe stamp bundle
../OctoSense-App-Hub/target/release/hub.exe check bundle --allow-unsigned
```

To go live with your own mailbox: run card-host, tap 添加账号, and type your
address + the provider's 授权码 into the **host's** sheet (QQ/163/Gmail
servers are auto-detected). The code is stored host-side under
`.local-state/.host/mail/` and never enters the app or the bundle.

### Inside the real OctoSense desktop shell (strongest demo)

One-time setup (see `../octosense-local-hub/README.md` for the full story):
build the shell from the local OctoSense checkout
(`python tools/setup.py`, then
`cargo build --release -p octosense --no-default-features --features app-hub`),
publish the bundle to the local hub, and launch with:

```sh
set MAKEPAD_REMOTE=8147
set OCTOSENSE_HUB_ANCHOR=<anchor public hex from ../octosense-local-hub/README>
set OCTOSENSE_APP_DATA=D:\Coding\Rust\agenticapp26\octosense-local-hub\device
start "" D:\Users\yzbtdiy\Cache\CARGO_TARGET\release\octosense.exe --test-action launch-hub:vibemail
python scripts/official_sheet_run.py 8147
```

The shell admits the bundle through its signature-verified catalog,
launches it as a window-manager client, and its own Mail service handles
`mail.*`: 添加账号 raises the official 「OctoSense · Add a mail account」
sheet (address / password / IMAP-vs-POP3 / server ports), and wrong
credentials are rejected by the real mail server (ev-19). The shell also
registers the `model` service, so in this environment the app's AI buttons
reach a real one-shot model call whenever the shell has providers
configured.

## Status

- `hub check` — `vibemail 0.5.4 — PASSED` (signed by the local hub working
  key; catalog sequence 2 in `../octosense-local-hub/`).
- Remaining human steps (publisher): `hub keygen` → `hub sign-manifest` →
  `hub check --publisher-key` → tag + open `Submit vibemail 0.5.4` on
  OctoSense-App-Hub with `evidence/hub/SUBMISSION.md` attached.
