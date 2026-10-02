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

echo '==> [1/2] service 单元测试'
python3 -m unittest discover -s service -v

echo '==> [2/2] hub check bundle --publisher-key (签名门禁)'
hub check bundle --publisher-key "$PUBLISHER_KEY"

echo '==> 验证通过'
