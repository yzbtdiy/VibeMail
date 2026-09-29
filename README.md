# Agentic Mail (agentic-mail)

English | [简体中文](README.zh-CN.md)

A concept app for the Agentic App Hackathon 2026 (mail scene). Five screens —
smart inbox, mail reading with an AI summary, AI drafting, follow-up todos and
profile — implemented as a Splash script app (`bundle/main.splash`) from the
four reference designs in `source/`, run for real in the App Hub `card-host`,
driven by real input, captured by real screenshots. The layout follows the
[OctoScript-App-Design-Flow examples](../OctoScript-App-Design-Flow/examples/README.md)
conventions (source / artwork / service / scripts / evidence).

**Capabilities & data**: the app requests `model` and `mail`.
`mail`: real sending/receiving goes through the platform's mail host service
(accounts are added on the host's own sheet; credentials stay in the system
vault, never in the app); where no service answers (card-host) the banner
says so and labelled practice data is used. `model`: AI summary and drafting
go through the one-shot model service (schema-checked, daily per-app budget)
using the model the person configured; keys never reach the app; fallbacks
are labelled. Todos are practice data (no-facts rule).

## Layout

```text
source/        design sources: design-01..04.png + design-brief.md (palette,
               per-screen spec, asset mapping, known deviations from the art)
artwork/       working copies of the SVG assets (shipped copies in bundle/assets/)
service/       reply-lifecycle reducer (controller.py — the verification twin of
               the main.splash state machine) + unittest (8 cases)
bridge/        DEV-ONLY: an IMAP/SMTP <-> loopback HTTP bridge (credentials live
               only in bridge/config.json, gitignored; 5 parsing unit tests)
dev/           DEV-ONLY: the bridge adapter that scripts/dev_bundle.py splices
               over the MARKER:ADAPTER block (never part of the submission)
scripts/       drive-demo.py — drives the real card-host window over the
               Makepad remote bridge through the full demo task
evidence/      run evidence: ev-01..08.png (reply lifecycle), final-snap.json,
               final-log.txt, hub/ (scan packet + SUBMISSION.md answers),
               l0-design/ (retired L0 card form), legacy/ (pre-redesign shots)
bundle/        THE SUBMISSION — main.splash, assets/, listing.json,
               manifest.json, screenshots/01..05 (hub check PASSED)
```

## Demo task (maps to the judging criteria)

识别 (AI triage + summary + attachment) → 提议 (editable AI draft, explicit
recipient, tone chips, quick replies) → 授权 (two-step confirmed send) →
结果核验 (sent strip in the read view, synced pill in the inbox) → 失败处理
(practice outage switch: send fails, draft kept, retry succeeds) → 真实模型调用
(ev-09/ev-10: card-host honestly answers `no service answers "model"` and the
UI says so; the same button produces real model output in an OctoSense desktop
Shell built from main ≥ 2026-09-28 with AI providers configured).

## Reproduce (Windows 10 26100 — the only platform tested)

```sh
python -m unittest discover -s service
../OctoSense-App-Hub/target/release/card-host.exe --bundle bundle \
    --app-data .local-state --allow-unsigned --stamp   # MAKEPAD_REMOTE=<port> for the bridge
python scripts/drive-demo.py <port>
../OctoSense-App-Hub/target/release/hub.exe check bundle --allow-unsigned
```

## Status

- `hub check` — `agentic-mail 0.1.0 — PASSED` (unsigned warning only).
- Remaining human steps (publisher): `hub keygen` → `hub sign-manifest` →
  `hub check --publisher-key` → tag + open `Submit agentic-mail 0.1.0` on
  OctoSense-App-Hub with `evidence/hub/SUBMISSION.md` attached.
