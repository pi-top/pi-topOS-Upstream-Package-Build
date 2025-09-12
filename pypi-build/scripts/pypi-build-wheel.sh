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
  local PACKAGE_NAME="$1"
  local VERSION="${2:-latest}"

  echo "Downloading ${PACKAGE_NAME} from PyPI, version: ${VERSION}"

  local CMD=(pypi-download "$PACKAGE_NAME")
  if [ "$VERSION" != "latest" ]; then
    CMD+=(--release "$VERSION")
  fi

  if ! "${CMD[@]}"; then
    echo "Failed to download ${PACKAGE_NAME} from PyPI"
    exit 1
  fi
}


function main() {
  local PACKAGE_NAME="${1}"
  local VERSION="${2}"
  local ARTIFACT_FOLDER="${3:-artifacts}"

  download_tar_from_pypi "${PACKAGE_NAME}" "${VERSION}"
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
  echo "Usage: $0 <package-name> <version> <dst-folder>"
  exit 1
fi

main "$1" "$2" "$3"
