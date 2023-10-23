FROM debian:bullseye

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y debhelper dh-python python3-all-dev python3-pip sudo libffi-dev libssl-dev pkg-config && \
    pip3 install stdeb requests click toml

RUN python3 -m pip install --upgrade pip

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

RUN pip3 install poetry

# Reinstall setuptools
# https://github.com/pypa/setuptools/issues/3269
#RUN pip3 install setuptools --force-reinstall

# Patch stdeb until https://github.com/astraw/stdeb/pull/195 is merged
COPY files/ /

# Add a user with userid 1000 and name nonroot
RUN useradd --create-home -u 1000 nonroot

# Configure sudo for nonroot
COPY sudoers.txt /etc/sudoers
RUN chmod 440 /etc/sudoers

# Run container as nonroot
USER nonroot

