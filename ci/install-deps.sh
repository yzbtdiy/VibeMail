#!/usr/bin/env bash
# VibeMail CI - 系统依赖(编译 hub 所需的 makepad Linux 依赖)
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

apt-get update -qq
apt-get install -y --no-install-recommends \
  pkg-config clang ca-certificates libssl-dev python3 \
  libx11-dev libxcursor-dev libxkbcommon-dev libxrandr-dev \
  libxi-dev libxinerama-dev \
  libasound2-dev libpulse-dev \
  libwayland-dev wayland-protocols \
  libegl1-mesa-dev libgl1-mesa-dev libgles2-mesa-dev libglx-dev \
  libdrm-dev libgbm-dev libgl1-mesa-dri mesa-vulkan-drivers \
  gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
  gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-gl \
  libgstreamer1.0-0 libgstreamer-plugins-base1.0-0 libgstreamer-gl1.0-0 \
  libfontconfig1-dev libfreetype6-dev

echo deps-ok
