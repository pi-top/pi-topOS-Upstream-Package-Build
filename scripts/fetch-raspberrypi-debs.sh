#!/bin/bash
# Downloads the packages in raspberrypi-boot/approved into the given directory,
# checking each against Raspberry Pi's signed package index.
set -euo pipefail

boot=$(cd "$(dirname "$0")/../raspberrypi-boot" && pwd)
out=${1:?usage: $0 <output directory>}
# shellcheck source-path=SCRIPTDIR source=../raspberrypi-boot/approved
source "$boot/approved"

archive=http://archive.raspberrypi.com/debian
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
mkdir -p "$out"

curl -fsS "$archive/dists/bookworm/InRelease" -o "$work/InRelease"
# Key CF8A1AF502A2AA2D763BAE7E82B129927FA3303E, from raspberrypi-archive-keyring
gpgv --keyring "$boot/raspberrypi-archive-keyring.gpg" --output "$work/Release" "$work/InRelease"

for arch in armhf arm64; do
  index=main/binary-$arch/Packages.gz
  sha=$(awk -v f="$index" '/^SHA256:/ {s = 1; next} /^[^ ]/ {s = 0} s && $3 == f {print $1}' "$work/Release")
  curl -fsS "$archive/dists/bookworm/$index" -o "$work/Packages-$arch.gz"
  echo "$sha  $work/Packages-$arch.gz" | sha256sum -c --quiet
  gzip -dc "$work/Packages-$arch.gz" > "$work/Packages-$arch"
done

fetch() { # package version architecture
  local stanza filename sha
  stanza=$(awk -v RS= -v p="$1" -v v="$2" '
    index($0, "Package: " p "\n") == 1 && index($0, "\nVersion: " v "\n") {print; exit}' \
    "$work/Packages-$3")
  if [ -z "$stanza" ]; then
    echo "$1 $2 ($3) is not in Raspberry Pi's package index" >&2
    return 1
  fi
  filename=$(sed -n 's/^Filename: //p' <<<"$stanza")
  sha=$(sed -n 's/^SHA256: //p' <<<"$stanza")
  curl -fsS "$archive/$filename" -o "$out/${filename##*/}"
  echo "$sha  $out/${filename##*/}" | sha256sum -c --quiet
  echo "${filename##*/}"
}

for p in $KERNEL_PACKAGES_ARMHF; do fetch "$p" "$KERNEL_VERSION" armhf; done
for p in $KERNEL_PACKAGES_ARM64; do fetch "$p" "$KERNEL_VERSION" arm64; done
fetch raspi-firmware "$RASPI_FIRMWARE_VERSION" armhf
fetch rpi-eeprom "$RPI_EEPROM_VERSION" armhf
