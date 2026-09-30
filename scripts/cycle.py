"""One-shot: restore 0.4.0 splash from git, rebuild with ui-new.splash,
restart the app, wait for boot, capture dark inbox."""
import subprocess, os, sys, time, json, urllib.request

ROOT = r'D:\Coding\Rust\agenticapp26\agentic-mail-card'
os.chdir(ROOT)

print(subprocess.run(['git', 'checkout', 'HEAD', '--', 'bundle/main.splash'],
                     capture_output=True, text=True).returncode)
r = subprocess.run([sys.executable, 'scripts/rebuild_ui.py'], capture_output=True, text=True)
print(r.stdout[-400:])
if r.returncode:
    print(r.stderr[-800:])
    sys.exit(1)

subprocess.run(['cmd', '/c', 'run.cmd stop'], capture_output=True, text=True)
subprocess.Popen(['cmd', '/c', 'run.cmd desktop'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

BASE = 'http://127.0.0.1:8146'

def get(path):
    with urllib.request.urlopen(BASE + path, timeout=10) as res:
        return res.read()

def widgets():
    d = json.loads(get('/snap'))
    return d['s'] if isinstance(d, dict) else d

for _ in range(80):
    try:
        if any('已整理今日' in w.get('t', '') for w in widgets() if w.get('ty') != 'Splash'):
            break
    except Exception:
        pass
    time.sleep(0.5)
else:
    raise SystemExit('no boot')

time.sleep(1.2)
last = get('/g?raw=1')
for _ in range(8):
    time.sleep(0.7)
    cur = get('/g?raw=1')
    if cur == last:
        break
    last = cur
open(os.path.join(ROOT, 'evidence', 'l0-design', 'v2-dark-inbox.png'), 'wb').write(last)
print('captured dark inbox')
