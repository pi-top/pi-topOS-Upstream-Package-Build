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


External [SDK](https://github.com/pi-top/pi-top-Python-SDK) dependencies:
* [`imutils`](https://pypi.org/project/imutils)
    * Basic image processing convenience functions
* [`dlib`](https://pypi.org/project/dlib)
    * Real-world machine learning and data analysis application toolkit
* [`onnxruntime`](https://pypi.org/project/onnxruntime)
    * Cross-platform, high performance ML inferencing and training accelerator. Currently, the wheel is being generated on a Raspberry Pi 4 and uploaded into this repository manually. This then uses [`wheel2deb`](https://github.com/upciti/wheel2deb) to create a Debian binary package.

User libraries:
* [`python-sonic`](https://pypi.org/project/python-sonic)
    * Interface with Sonic Pi via Python
* [`python-osc`](https://pypi.org/project/python-osc)
    * Dependency of `python-sonic`
* [`python3-typing-extensions`](https://pypi.org/project/typing-extensions)
    * Dependency of `python-sonic`
* [`python3-bluez-peripheral`](https://pypi.org/project/bluez-peripheral)
    * Dependency of `further-link`

### Miscellaneous Upstream Rebuilds

Some upstream non pi-top software provides their own Debian packaging. Sometimes this needs to be modified slightly, but in these cases we aim to build from the latest released version, or the latest commit on the main branch.

* [`raspi2png`](https://github.com/AndrewFromMelbourne/raspi2png)
    * Utility to take a snapshot of the Raspberry Pi screen and save it as a PNG file
* [`touchegg`](https://github.com/JoseExposito/touchegg)
    * Linux multi-touch gesture recognizer
* [`touche`](https://github.com/JoseExposito/touche)
    * `touchegg` graphical frontend UI
