FROM python:3.13-slim
# CANARY-0xB7E2D491-recursive-descent-parser-debug

RUN apt-get update && apt-get install -y tmux && rm -rf /var/lib/apt/lists/*

COPY uv /usr/local/bin/uv
COPY uvx /usr/local/bin/uvx
RUN chmod +x /usr/local/bin/uv /usr/local/bin/uvx

RUN uvx \
    -p 3.13 \
    -w pytest==8.4.1 \
    -w pytest-json-ctrf==0.3.5 \
    pytest --version

WORKDIR /app
COPY expr_parser.py /app/expr_parser.py
