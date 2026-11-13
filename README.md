# pi-topOS Upstream Package Build

This repository is used for building and uploading Debian source and binary packages into the pi-topOS apt repository that are not pi-top software. This can be external dependencies for pi-top software, or libraries/apps that are intended for use by the end-user.

## Packages

### ARMv7 contamination

Raspberry Pi OS does not provide packages that are not guaranteed to run on ARMv6, which is needed for earlier Raspberry Pi models that are not officially supported by pi-topOS.

Qt 5's [WebEngine](https://doc.qt.io/qt-5/qtwebengine-overview.html) component is provided by multiple Debian binary packages produced from the source [`qtwebengine-opensource-src`](https://packages.debian.org/source/stable/qtwebengine-opensource-src) package that fail this check and are consequently not available directly in pi-topOS:

* [`libqt5webengine5`](https://packages.debian.org/stable/libqt5webengine5)
* [`libqt5webenginecore5`](https://packages.debian.org/stable/libqt5webenginecore5)
* [`libqt5webenginewidgets5`](https://packages.debian.org/stable/libqt5webenginewidgets5)
* [`qml-module-qtwebengine`](https://packages.debian.org/stable/qml-module-qtwebengine)

### Python

Where possible, Python packages are repackaged for Debian via [`stdeb`](https://github.com/astraw/stdeb) from their source tarball on PyPI.

Packages that need [`wheel2deb`](https://github.com/upciti/wheel2deb) are built by `wheel-deb-build.yml` from `wheels/<package>/<arch>/bookworm/`, which holds either:

* a `requirements.txt` pinning a PyPI release (or a URL) by hash. A pinned sdist is built into a wheel natively for that architecture (armhf and arm64 on GitHub's arm64 runner); a pinned wheel is used as is. Or:
* a single committed wheel (older packages, built elsewhere).

A `wheel2deb.yml` in the same folder sets the Debian revision. Bump it when rebuilding a version that's already been published.

Compiled armhf packages must target ARMv7, the armhf baseline. `scripts/check-armhf-elf.sh` fails the build if any doesn't, since native builds run on an ARMv8 CPU.


External [SDK](https://github.com/pi-top/pi-top-Python-SDK) dependencies:
* [`imutils`](https://pypi.org/project/imutils)
    * Basic image processing convenience functions
* [`dlib`](https://pypi.org/project/dlib)
    * Real-world machine learning and data analysis application toolkit
* [`onnxruntime`](https://pypi.org/project/onnxruntime)
    * Cross-platform, high performance ML inferencing and training accelerator, used by the SDK's emotion classifier. arm64 uses the official PyPI wheel. No armv7 wheel exists upstream, so `onnxruntime-wheel-build.yml` builds one from the release tag natively on GitHub's arm64 runner; running it by hand on master publishes the wheel as a release of this repo.

User libraries:
* [`python-sonic`](https://pypi.org/project/python-sonic)
    * Interface with Sonic Pi via Python.
* [`python-osc`](https://pypi.org/project/python-osc)
    * Dependency of `python-sonic`.
* [`python3-bluez-peripheral`](https://pypi.org/project/bluez-peripheral)
    * Dependency of `further-link`.
* [`python3-dbus-fast`](https://pypi.org/project/dbus-fast)
    * Dependency of `python3-bluez-peripheral`.
* [`python3-nmcli`](https://pypi.org/project/nmcli)
    * Dependency of `pt-os-web-portal` to interact with `NetworkManager` .

### Miscellaneous Upstream Rebuilds

Some upstream non pi-top software provides their own Debian packaging. Sometimes this needs to be modified slightly, but in these cases we aim to build from the latest released version, or the latest commit on the main branch.

* [`touchegg`](https://github.com/JoseExposito/touchegg)
    * Linux multi-touch gesture recognizer
* [`touche`](https://github.com/JoseExposito/touche)
    * `touchegg` graphical frontend UI
