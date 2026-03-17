FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    gcc libssl-dev tmux \
    && rm -rf /var/lib/apt/lists/*

COPY uv /usr/local/bin/uv
COPY uvx /usr/local/bin/uvx
RUN chmod +x /usr/local/bin/uv /usr/local/bin/uvx

RUN uvx \
  -p 3.13 \
  -w pytest==8.4.1 \
  -w pytest-json-ctrf==0.3.5 \
  pytest --version

WORKDIR /app

COPY auth_key.txt /app/auth_key.txt

# Compile and strip the server binary, then remove source
COPY server.c /app/server.c
RUN gcc -O2 -o /app/ghost_server /app/server.c -lssl -lcrypto && \
    strip /app/ghost_server && \
    rm /app/server.c

# Generate the PCAP capture using scapy, then remove source and scapy
RUN pip install --break-system-packages scapy==2.6.1
COPY gen_capture.py /app/gen_capture.py
RUN python3 /app/gen_capture.py && rm /app/gen_capture.py
RUN pip uninstall -y scapy 2>/dev/null || true
