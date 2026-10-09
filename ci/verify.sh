#!/usr/bin/env bash
# VibeMail CI - Linux 构建验证(制品镜像快速路径)
#
# 背景:app-contract 1.x 起 hub 的 bundle 摘要是跨平台可移植口径(相对路径以
# 正斜杠计入哈希、按路径分量排序——app-contract/src/bundle.rs portable_path),
# Windows 与 Linux 计算一致。0.7.26 起本仓库按该口径盖章;提交通道为 GitHub
# publisher 工作流(.github/workflows/publish-app.yml),可编辑源码保持未签名,
# 最终证明清单由 tag 工作流生成。本脚本做等价三步验证:
#   1) service 单元测试
#   2) Python 按可移植口径重算 blake3 目录摘要,与 manifest 声明严格比对
#   3) hub check bundle --allow-unsigned —— Linux 侧完整结构门禁
set -euo pipefail

cd "$(dirname "$0")/.."

echo '==> hub 工具(制品镜像烘焙)'
command -v hub || { echo 'hub 不在 PATH:需要 octo-env 制品镜像' >&2; exit 1; }

echo '==> [1/3] service 单元测试'
python3 -m unittest discover -s service -v

echo '==> [2/3] 可移植摘要复验 (与清单声明严格比对)'
python3 -m pip install --quiet --break-system-packages blake3 2>/dev/null || \
  { apt-get update -qq && apt-get install -y -qq python3-pip >/dev/null \
    && python3 -m pip install --quiet --break-system-packages blake3; }
python3 - <<'EOF'
import json, pathlib, sys
import blake3

root = pathlib.Path('bundle')

# portable_path: '/' between components; digest order is path-component order
rels = [p.relative_to(root).as_posix()
        for p in root.rglob('*')
        if p.is_file() and p.name != 'manifest.json']
rels.sort(key=lambda r: r.split('/'))
h = blake3.blake3()
for rel in rels:
    b = (root / rel).read_bytes()
    h.update(rel.encode())
    h.update(b'\x00')
    h.update(len(b).to_bytes(8, 'little'))
    h.update(b)
computed = h.hexdigest()
claim = json.loads((root / 'manifest.json').read_text())['integrity']['bundle_blake3'].lower()
print(f'computed: {computed}')
print(f'claimed : {claim}')
sys.exit(0 if computed == claim else 'digest mismatch')
EOF

echo '==> [3/3] hub 结构门禁 (--allow-unsigned;可编辑源码未签名)'
hub check bundle --allow-unsigned

echo '==> Linux 构建验证全部通过'
