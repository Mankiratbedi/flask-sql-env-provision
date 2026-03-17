FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    gawk \
    tmux \
    && rm -rf /var/lib/apt/lists/*

# Pre-install uv/uvx for offline test execution
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

# Generate the auth.log data file at build time
COPY generate_logs.py /tmp/generate_logs.py
RUN python3 /tmp/generate_logs.py > /app/auth.log \
    && echo "Generated $(wc -l < /app/auth.log) log lines" \
    && rm /tmp/generate_logs.py
