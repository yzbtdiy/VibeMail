#!/usr/bin/env bash
# VibeMail CI - 检出 OctoSense 工具链并锁定运行时版本
# App Hub 的 Cargo.toml 以同级目录(../makepad 等)解析依赖,
# 因此四个检出互为同级,统一放在 /toolchain 下
set -euo pipefail

TC="${TOOLCHAIN_DIR:-/toolchain}"
GITHUB_PREFIX="${GITHUB_URL_PREFIX:-}"

clone_repo() { # clone_repo <owner/repo> <目录> [git参数...]
  local repo="$1" dir="$2"; shift 2
  if [ -d "$dir/.git" ]; then echo "[skip] $dir"; return 0; fi
  if [ -n "$GITHUB_PREFIX" ]; then
    git clone "$@" "${GITHUB_PREFIX}https://github.com/${repo}.git" "$dir" \
      || git clone "$@" "https://github.com/${repo}.git" "$dir"
  else
    git clone "$@" "https://github.com/${repo}.git" "$dir"
  fi
}

mkdir -p "$TC"
clone_repo OctoSense-org/OctoScript-App-Design-Flow "$TC/OctoScript-App-Design-Flow" --depth 1
clone_repo OctoSense-org/OctoSense-App-Hub "$TC/OctoSense-App-Hub" --depth 1

# 按 native-runtime.lock.json 浅取 makepad / octoscript / octoscript-makepad 并校验
cd "$TC/OctoScript-App-Design-Flow"
python3 tools/setup-native.py
python3 tools/setup-native.py --check

echo checkout-ok
