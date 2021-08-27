#!/bin/bash
###############################################################
#                Unofficial 'Bash strict mode'                #
# http://redsymbol.net/articles/unofficial-bash-strict-mode/  #
###############################################################
set -euo pipefail
IFS=$'\n\t'
###############################################################

if [[ -n "${BUILD_DEPENDENCIES:-}" ]]; then
  apt-get install -y ${BUILD_DEPENDENCIES:-}
fi

package_name="${1}"
shift

tarball_file_name="$(pypi-download "${package_name}" | awk '{print $2}')"

cwd=$(pwd)

tar xvzf "${cwd}/${tarball_file_name}"
mv "./$(echo "${tarball_file_name}" | sed 's/.tar.gz//')/"* .

patch_file_path="${cwd}/pypi-build/patches/${package_name}.patch"
echo "Looking for patch: ${patch_file_path}"
ls

if [[ -f "${patch_file_path}" ]]; then
  echo "Patch found: ${patch_file_path}"
  patch_file_args="--stdeb-patch-file=${patch_file_path} "
fi

set -x
python3 setup.py --command-packages stdeb.command sdist_dsc ${patch_file_args:-}${@} --dist-dir=./artifacts bdist_deb
