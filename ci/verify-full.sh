#!/usr/bin/env bash
# VibeMail CI - 自包含慢速路径(不依赖制品镜像时使用,约60-90分钟)
# 前置:rust:1-bookworm 镜像 + 先运行 ci/install-deps.sh 与 ci/setup-toolchain.sh
set -euo pipefail

TC="${TOOLCHAIN_DIR:-/toolchain}"
HUB="$TC/OctoSense-App-Hub/target/release/hub"
PUBLISHER_KEY="${VIBEMAIL_PUBLISHER_KEY:-yzbtdiy=1095438c3939742da32f74fbcc724ae452b3f1e22e4ebe9cd834c24b2b2b5759}"

echo '==> [1/3] cargo build --release -p octosense-app-hub --bin hub'
cargo build --release \
  --manifest-path "$TC/OctoSense-App-Hub/Cargo.toml" \
  -p octosense-app-hub --bin hub
test -x "$HUB"

echo '==> [2/3] service 单元测试'
cd "$(dirname "$0")/.."
python3 -m unittest discover -s service -v

echo '==> [3/3] hub check bundle --publisher-key (签名门禁)'
"$HUB" check bundle --publisher-key "$PUBLISHER_KEY"

echo '==> 验证通过'
