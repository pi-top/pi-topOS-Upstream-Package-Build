#!/bin/bash -ex

function build() {
  local PKG_FOLDER="${1}"
  
  # Build
  cd "${PKG_FOLDER}"
  if ! python3 -m build --wheel; then
    echo "Failed to build ${PKG_FOLDER}"
    exit 1
  fi
  cd -
}

function extract_tarball() {
  local TAR_FILE="${1}"
  local FOLDER="${2}"

  # Remove folder if exists  
  if [ -d "${FOLDER}" ]; then
    rm -rf "${FOLDER}"
  fi

  # Extract tarball
  tar -xf "${TAR_FILE}"
}

function download_tar_from_pypi() {
  # Download tarball
  if ! pypi-download "${1}"; then
    echo "Failed to download ${1} from PyPI"
    exit 1
  fi
}


function main() {
  local PACKAGE_NAME="${1}"
  local ARTIFACT_FOLDER="${2:-artifacts}"

  download_tar_from_pypi "${PACKAGE_NAME}"
  TARBALL=$(find . -name "*.tar.gz" | head -n 1)
  FOLDER=$(basename "${TARBALL}" .tar.gz)
  
  extract_tarball "${TARBALL}" "${FOLDER}"
  build "${FOLDER}"
  WHEEL_PATH=$(find "${FOLDER}/dist" -name "*.whl" | head -n 1)

  # Move wheel to artifacts folder
  mkdir -p "${ARTIFACT_FOLDER}"
  mv "${WHEEL_PATH}" "${ARTIFACT_FOLDER}/"
  chmod a+r "${ARTIFACT_FOLDER}"/*.whl

  # Cleanup
  rm -r "${FOLDER}" "${TARBALL}" || true
}


if [ $# -lt 1 ]; then
  echo "Usage: $0 <package-name> <dst-folder>"
  exit 1
fi

main "$1" "$2"
