# Use an official Golang runtime as a parent image
FROM golang:1.17.8-stretch AS builder

# Set the working directory to /go/src/app
WORKDIR /go/src/app

# Clone the Go source code from GitHub
RUN git clone --depth=1 --branch testing https://github.com/niloysh/go-gtp5gnl

# Build the gogtp5g-tunnel executable
RUN cd go-gtp5gnl/cmd/gogtp5g-tunnel && CGO_ENABLED=0 GOOS=linux go build -a -ldflags="-s -w"

# Use a smaller base image
FROM python:3.9.10-slim-buster

LABEL maintainer="Niloy Saha <niloysaha.ns@gmail.com>"
LABEL description="UPF stats exporter v4.0"

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN apt-get update \
    && apt-get -y install vim iproute2 curl \
    && apt-get clean

RUN pip install --no-cache-dir prometheus_client

COPY --from=builder /go/src/app/go-gtp5gnl/cmd/gogtp5g-tunnel/gogtp5g-tunnel /app/

COPY /app/* ./

RUN chmod +x upf-exporter.py

EXPOSE 9000

CMD ["python", "upf-exporter.py"]