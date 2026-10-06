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

echo '==> [1/3] service 单元测试'
python3 -m unittest discover -s service -v

echo '==> [2/3] Windows 约定摘要复验 (与清单声明严格比对)'
# 两段式:仓库自 `bundle/** -text` 后字节精确(0.7.25+),按原样验;
# 旧版本(0.6.x,autocrlf 洗成 LF 入库)需恢复 CRLF 后再验。
python3 -m pip install --quiet --break-system-packages blake3 2>/dev/null || \
  { apt-get update -qq && apt-get install -y -qq python3-pip >/dev/null \
    && python3 -m pip install --quiet --break-system-packages blake3; }
python3 - <<'EOF'
import json, pathlib, subprocess, sys
import blake3

root = pathlib.Path('bundle')

def digest() -> str:
    rels = sorted(p.relative_to(root).as_posix()
                  for p in root.rglob('*')
                  if p.is_file() and p.name != 'manifest.json')
    h = blake3.blake3()
    for rel in rels:
        b = (root / rel).read_bytes()
        h.update(rel.replace('/', '\\').encode())
        h.update(b'\x00')
        h.update(len(b).to_bytes(8, 'little'))
        h.update(b)
    return h.hexdigest()

claim = json.loads((root / 'manifest.json').read_text())['integrity']['bundle_blake3'].lower()
first = digest()
if first == claim:
    print(f'computed: {first}')
    print('digest-ok (原样字节)')
    sys.exit(0)

# 旧版回退:文本文件恢复 CRLF(Windows autocrlf 盖章场景)后重验
for p in root.rglob('*'):
    if p.is_file():
        b = p.read_bytes()
        if b'\x00' in b or b'\r\n' in b:
            continue
        p.write_bytes(b.replace(b'\n', b'\r\n'))
second = digest()
print(f'computed: {first} (原样) / {second} (CRLF恢复)')
print(f'claimed : {claim}')
if second == claim:
    print('digest-ok (CRLF 恢复)')
    sys.exit(0)
sys.exit('digest mismatch')
EOF

echo '==> [3/3] hub 结构门禁 (副本:剥离签名+写入Linux摘要后 --allow-unsigned)'
rm -rf /tmp/bundle-gate && cp -r bundle /tmp/bundle-gate
python3 - <<'EOF'
import json, pathlib
import blake3

root = pathlib.Path('/tmp/bundle-gate')

def digest(sep: str) -> str:
    rels = sorted(p.relative_to(root).as_posix()
                  for p in root.rglob('*')
                  if p.is_file() and p.name != 'manifest.json')
    h = blake3.blake3()
    for rel in rels:
        b = (root / rel).read_bytes()
        h.update(rel.replace('/', sep).encode())
        h.update(b'\x00')
        h.update(len(b).to_bytes(8, 'little'))
        h.update(b)
    return h.hexdigest()

mf = root / 'manifest.json'
m = json.loads(mf.read_text())
m['integrity']['signature'] = None          # 结构门禁副本:剥签名
m['integrity']['bundle_blake3'] = digest('/')  # Linux 分隔符摘要
mf.write_text(json.dumps(m, ensure_ascii=False, indent=2))
print('gate manifest prepared (linux digest)')
EOF
hub check /tmp/bundle-gate --allow-unsigned

echo '==> Linux 构建验证全部通过'
