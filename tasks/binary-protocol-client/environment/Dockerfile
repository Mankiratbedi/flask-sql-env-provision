FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    curl tmux build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Build server binary from source; do not leave server.c in image
COPY server.c capture.pcap ./
RUN gcc -o server server.c && strip server && rm server.c

# Pre-install uv/uvx for offline test execution (Harbor disables internet)
# Before building: cp $(which uv) $(which uvx) tasks/binary-protocol-client/environment/
COPY uv /usr/local/bin/uv
COPY uvx /usr/local/bin/uvx
RUN chmod +x /usr/local/bin/uv /usr/local/bin/uvx

# Pre-cache the pytest uvx environment so it works offline
RUN uvx \
    -p 3.13 \
    -w pytest==8.4.1 \
    -w pytest-json-ctrf==0.3.5 \
    pytest --version

# Image contains only server binary and capture.pcap in /app
