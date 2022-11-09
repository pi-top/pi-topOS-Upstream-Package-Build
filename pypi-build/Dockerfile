FROM debian:bullseye

RUN apt-get update && \
    apt-get install -y debhelper dh-python python3-all-dev python3-pip sudo && \
    pip3 install stdeb requests click

# Add a user with userid 1000 and name nonroot
RUN useradd --create-home -u 1000 nonroot

# Configure sudo for nonroot
COPY  sudoers.txt /etc/sudoers
RUN chmod 440 /etc/sudoers

# Run container as nonroot
USER nonroot
