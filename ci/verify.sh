#!/usr/bin/env bash
# VibeMail CI - Linux 构建验证(制品镜像快速路径)
# 镜像 docker.cnb.cool/opensource.cool/octo-env:latest 已烘焙 hub;
# 慢速自包含路径见 ci/verify-full.sh
set -euo pipefail

# 发行者公钥(hex)——README 门禁复现命令同款,非私钥
PUBLISHER_KEY="${VIBEMAIL_PUBLISHER_KEY:-yzbtdiy=1095438c3939742da32f74fbcc724ae452b3f1e22e4ebe9cd834c24b2b2b5759}"

cd "$(dirname "$0")/.."

echo '==> hub 工具(制品镜像烘焙)'
command -v hub || {
  echo 'hub 不在 PATH:本流水线需要 octo-env 制品镜像;或改用 ci/verify-full.sh 自包含构建' >&2
  exit 1
}

echo '==> 恢复发行者盖章字节 (Windows autocrlf: 文本文件按 CRLF 盖章签名)'
# 签名时的工作区是 autocrlf 检出的 CRLF 字节,入库被转为 LF;
# Linux 检出为 LF 导致摘要不匹配。这里把 bundle 内文本文件恢复为
# CRLF 字节(等价于发行者的 Windows 检出),签名验证才对着盖章字节进行。
python3 - <<'EOF'
import pathlib
root = pathlib.Path('bundle')
changed = []
for p in root.rglob('*'):
    if not p.is_file():
        continue
    b = p.read_bytes()
    if b'\x00' in b:            # 二进制(PNG 等)不动
        continue
    if b'\r\n' in b:            # 已是 CRLF
        continue
    p.write_bytes(b.replace(b'\n', b'\r\n'))
    changed.append(str(p))
print(f'crlf-restored: {len(changed)} file(s)')
EOF

echo '==> [1/2] service 单元测试'
python3 -m unittest discover -s service -v

echo '==> [2/2] hub check bundle --publisher-key (签名门禁)'
hub check bundle --publisher-key "$PUBLISHER_KEY"

echo '==> 验证通过'
