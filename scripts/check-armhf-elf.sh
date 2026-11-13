#!/bin/bash
# Fail if any ELF file in the given .deb or .whl packages targets newer than ARMv7,
# the armhf baseline. Native builds on the arm64 runner see an ARMv8 CPU.
set -euo pipefail
status=0
for pkg in "$@"; do
  dir="$(mktemp -d)"
  case "${pkg}" in
    *.deb) dpkg-deb -x "${pkg}" "${dir}" ;;
    *.whl) unzip -q "${pkg}" -d "${dir}" ;;
    *) echo "::error::Unknown package type: ${pkg}"; exit 1 ;;
  esac
  while IFS= read -r -d '' f; do
    [ "$(head -c 4 "${f}" | od -An -tx1 | tr -d ' \n')" = 7f454c46 ] || continue
    arch="$(readelf -A "${f}" | sed -n 's/^ *Tag_CPU_arch: *//p')"
    case "${arch}" in
      v4*|v5*|v6*|v7) echo "${arch} ${f#"${dir}"/}" ;;
      *) echo "::error::${pkg}: ${f#"${dir}"/} targets '${arch:-not ARM32}'"; status=1 ;;
    esac
  done < <(find "${dir}" -type f -print0)
  rm -rf "${dir}"
done
exit "${status}"
