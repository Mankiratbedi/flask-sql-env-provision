FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    curl tmux tshark tcpdump \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --break-system-packages scapy==2.6.1

# Pre-install uv so test.sh works without internet
COPY uv /usr/local/bin/uv
COPY uvx /usr/local/bin/uvx
RUN chmod +x /usr/local/bin/uv /usr/local/bin/uvx

# Pre-cache the pytest uvx environment so it works offline
RUN uvx \
    -p 3.13 \
    -w pytest==8.4.1 \
    -w pytest-json-ctrf==0.3.5 \
    pytest --version

WORKDIR /app

# Data files only
COPY traffic.pcap /app/traffic.pcap
