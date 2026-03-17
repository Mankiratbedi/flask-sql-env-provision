FROM python:3.13-slim
# CANARY-0xA3F1C8D2-autograd-engine-debug

RUN apt-get update && apt-get install -y tmux && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir numpy==2.2.3

COPY uv /usr/local/bin/uv
COPY uvx /usr/local/bin/uvx
RUN chmod +x /usr/local/bin/uv /usr/local/bin/uvx

RUN uvx \
    -p 3.13 \
    -w pytest==8.4.1 \
    -w pytest-json-ctrf==0.3.5 \
    -w numpy==2.2.3 \
    pytest --version

WORKDIR /app
COPY autograd_engine.py /app/autograd_engine.py
