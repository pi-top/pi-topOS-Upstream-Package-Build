FROM debian:sid

RUN apt-get update && \
    apt-get install -y debhelper dh-python python3-all-dev python3-pip && \
    pip3 install stdeb requests

COPY scripts/pypi-build.sh /pypi-build

ENTRYPOINT ["/pypi-build"]