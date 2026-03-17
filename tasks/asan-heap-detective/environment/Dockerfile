FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    gcc tmux \
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

COPY kvstore.c /app/kvstore.c
COPY trigger.txt /app/trigger.txt

# Generate ASAN trace by compiling with sanitizer and running the trigger
RUN gcc -fsanitize=address -g -o /app/kvstore_asan /app/kvstore.c && \
    (/app/kvstore_asan < /app/trigger.txt > /dev/null 2> /app/asan_trace.txt || true) && \
    rm /app/kvstore_asan
