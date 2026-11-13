#!/bin/bash
# Build an onnxruntime wheel from a release tag, inside debian:bookworm on armhf.
# Usage: build-wheel.sh <version> <commit> <output dir>
set -euxo pipefail
version="$1"
commit="$2"
out="$3"

# onnxruntime needs CMake 3.26; bookworm has 3.25
echo "deb http://deb.debian.org/debian bookworm-backports main" > /etc/apt/sources.list.d/backports.list
apt-get update
apt-get install -y --no-install-recommends build-essential git ca-certificates \
  python3-dev python3-numpy python3-pip python3-setuptools python3-wheel python3-packaging
apt-get install -y --no-install-recommends -t bookworm-backports cmake

git clone --depth 1 --branch "v${version}" https://github.com/microsoft/onnxruntime /src
test "$(git -C /src rev-parse HEAD)" = "${commit}"

# GitLab regenerated the Eigen archive the release pins by SHA1, so fetch the
# same commit by id instead (onnxruntime's cmake/deps.txt names it)
eigen_commit="$(sed -n 's#^eigen;.*/archive/\([0-9a-f]\{40\}\)/.*#\1#p' /src/cmake/deps.txt)"
git init /eigen
git -C /eigen fetch --depth 1 https://gitlab.com/libeigen/eigen.git "${eigen_commit}"
git -C /eigen checkout FETCH_HEAD

cd /src
# 32-bit on an arm64 kernel reports armv8l, which wheel2deb treats as arch all
export _PYTHON_HOST_PLATFORM=linux-armv7l
# Without linux32, uname -m says aarch64 and CMake builds the 64-bit ARM code paths
setarch linux32 uname -m
setarch linux32 ./build.sh --config Release --update --build --build_wheel \
  --parallel "$(nproc)" --skip_tests --allow_running_as_root --compile_no_warning_as_error \
  --cmake_extra_defines onnxruntime_BUILD_UNIT_TESTS=OFF FETCHCONTENT_SOURCE_DIR_EIGEN=/eigen

cp build/Linux/Release/dist/*.whl "${out}/"
