FROM python:3.13-slim

RUN apt-get update && apt-get install -y tmux sqlite3 && rm -rf /var/lib/apt/lists/*

COPY uv /usr/local/bin/uv
COPY uvx /usr/local/bin/uvx
RUN chmod +x /usr/local/bin/uv /usr/local/bin/uvx

RUN uvx -p 3.13 -w pytest==8.4.1 -w pytest-json-ctrf==0.3.5 pytest --version

WORKDIR /app

COPY queries.sql /app/queries.sql
COPY benchmark.py /app/benchmark.py
COPY setup_db.py /app/setup_db.py
RUN python3 /app/setup_db.py && rm /app/setup_db.py
