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

# Compile and strip the hash oracle binary, then remove source
COPY hash_oracle.c /app/hash_oracle.c
RUN gcc -O2 -o /app/hash_oracle /app/hash_oracle.c && \
    strip /app/hash_oracle && \
    rm /app/hash_oracle.c
