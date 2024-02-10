# Build stage for Free5GC
FROM golang:1.14.4-stretch AS builder
LABEL maintainer="Niloy Saha <niloysaha.ns@gmail.com>"

# Rename repo after Debian bulls-eye release
RUN sed -i 's/stable\/updates/stable-security\/updates/' /etc/apt/sources.list \
    && sed -i s/deb.debian.org/archive.debian.org/g /etc/apt/sources.list \
    && sed -i 's|security.debian.org|archive.debian.org|g' /etc/apt/sources.list \
    && sed -i '/stretch-updates/d' /etc/apt/sources.list



# Install dependencies for building Free5GC
RUN apt-get update \
    && apt-get -y install gcc cmake autoconf libtool pkg-config libmnl-dev libyaml-dev apt-transport-https ca-certificates \
    && curl -sL https://deb.nodesource.com/setup_14.x | bash - \
    && curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - \
    && echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list \
    && apt-get update \
    && apt-get install -y nodejs yarn \
    && apt-get clean

# Get and build Free5GC
RUN cd $GOPATH/src \
    && git clone --recursive -b v3.2.0 -j `nproc` https://github.com/free5gc/free5gc.git \
    && cd free5gc \
    && make all

# Final stage based on Ubuntu 20.04
FROM ubuntu:20.04
LABEL maintainer="Niloy Saha <niloysaha.ns@gmail.com>"
LABEL description="Free5GC v3.2.0"
ENV DEBIAN_FRONTEND=noninteractive

# Install runtime dependencies
RUN apt-get update \
    && apt-get -y install vim net-tools curl libmnl0 libyaml-0-2 iproute2 iptables tcpdump iputils-ping \
    && apt-get clean

WORKDIR /free5gc
RUN mkdir -p config/ log/ config/TLS/ public/

# Copy artifacts from builder stage
COPY --from=builder /go/src/free5gc/bin/* ./
COPY --from=builder /go/src/free5gc/webconsole/bin/webconsole ./webui
COPY --from=builder /go/src/free5gc/webconsole/public ./public
COPY --from=builder /go/src/free5gc/config/* ./config/
COPY --from=builder /go/src/free5gc/config/TLS/* ./config/TLS/

VOLUME [ "/free5gc/config"]

# Expose necessary ports
EXPOSE 8000 5000
