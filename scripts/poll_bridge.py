import json
import sys
import time
import urllib.request

port = sys.argv[1] if len(sys.argv) > 1 else "8147"
base = f"http://127.0.0.1:{port}"

for _ in range(40):
    try:
        with urllib.request.urlopen(base + "/snap", timeout=5) as r:
            ws = json.loads(r.read().decode("utf-8"))["s"]
        print(len(ws), "widgets")
        shown = 0
        for w in ws:
            t = w.get("t", "")
            if t and not t.startswith("//") and not t.startswith("let ") and shown < 60:
                print(" -", w.get("ty", ""), w["r"][:4], repr(t.replace("\n", " ")[:56]))
                shown += 1
        break
    except Exception:
        time.sleep(1)
else:
    print("NO BRIDGE on", base)
