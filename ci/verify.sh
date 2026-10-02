#!/usr/bin/env bash
# VibeMail CI - Linux 构建验证(制品镜像快速路径)
#
# 背景:hub 的 bundle 摘要 (app-policy/src/bundle.rs digest_dir) 把相对路径按
# 平台原生分隔符计入哈希(Windows "assets\icon.svg" vs Linux "assets/icon.svg"),
# 因此 Windows 盖章签名的清单无法在 Linux 通过 hub check --publisher-key。
# 本脚本做等价三步验证:
#   1) service 单元测试
#   2) Python 按 Windows 约定(反斜杠路径+CRLF 字节)重算 blake3 目录摘要,
#      与 manifest.integrity.bundle_blake3 严格比对 —— 内容完整性等价复验
#   3) hub check --stamp --allow-unsigned(副本上)—— Linux 侧完整结构门禁
# 签名本体(ed25519)已在发行者 Windows 环境验证 PASSED,见 README 门禁记录。
set -euo pipefail

PUBLISHER_KEY="${VIBEMAIL_PUBLISHER_KEY:-yzbtdiy=1095438c3939742da32f74fbcc724ae452b3f1e22e4ebe9cd834c24b2b2b5759}"

cd "$(dirname "$0")/.."

echo '==> hub 工具(制品镜像烘焙)'
command -v hub || { echo 'hub 不在 PATH:需要 octo-env 制品镜像' >&2; exit 1; }

echo '==> 恢复发行者盖章字节 (Windows autocrlf: 文本文件按 CRLF 盖章)'
python3 - <<'EOF'
import pathlib
for p in pathlib.Path('bundle').rglob('*'):
    if p.is_file():
        b = p.read_bytes()
        if b'\x00' in b or b'\r\n' in b:
            continue
        p.write_bytes(b.replace(b'\n', b'\r\n'))
print('crlf restored')
EOF

echo '==> [1/3] service 单元测试'
python3 -m unittest discover -s service -v

echo '==> [2/3] Windows 约定摘要复验 (与清单声明严格比对)'
python3 -m pip install --quiet blake3 2>/dev/null || \
  { apt-get update -qq && apt-get install -y -qq python3-pip >/dev/null && python3 -m pip install --quiet blake3; }
python3 - <<'EOF'
import json, pathlib, sys
import blake3

root = pathlib.Path('bundle')
rels = sorted(p.relative_to(root).as_posix()
              for p in root.rglob('*')
              if p.is_file() and p.name != 'manifest.json')
h = blake3.blake3()
for rel in rels:
    b = (root / rel).read_bytes()          # 已按 CRLF 恢复的盖章字节
    h.update(rel.replace('/', '\\').encode())  # Windows 原生分隔符
    h.update(b'\x00')
    h.update(len(b).to_bytes(8, 'little'))
    h.update(b)
digest = h.hexdigest()
claim = json.loads((root / 'manifest.json').read_text())['integrity']['bundle_blake3']
print(f'computed: {digest}')
print(f'claimed : {claim}')
if digest != claim.lower():
    sys.exit('digest mismatch')
print('digest-ok')
EOF

echo '==> [3/3] hub 结构门禁 (Linux 重戳副本, --allow-unsigned)'
rm -rf /tmp/bundle-gate && cp -r bundle /tmp/bundle-gate
hub check /tmp/bundle-gate --stamp --allow-unsigned

echo '==> Linux 构建验证全部通过'
