@echo off
rem VibeMail one-command runner. Everything lives in scripts\run_app.py;
rem this wrapper only makes it double-clickable from the repo root.
rem
rem   run.cmd              launch the app in card-host at phone width (412x860)
rem   run.cmd desktop      ... at desktop width (1200x860, master-detail)
rem   run.cmd demo         phone width + the FULL evidence run (drive-demo.py)
rem   run.cmd mail         store-form mail flow (drive-mail.py: sheet -> real rejection)
rem   run.cmd shell        the real OctoSense desktop shell (local signed hub)
rem   run.cmd shell-drive  shell + official_sheet_run.py (ev-17..19 flow)
rem   run.cmd check        unit tests + hub stamp + hub gate check
rem   run.cmd stop         kill every test instance (card-host / octosense)
python "%~dp0scripts\run_app.py" %*
