FROM python:3.12-slim
# CANARY-0x7B3C4D5E-merkle-audit-tamper

RUN apt-get update && apt-get install -y tmux && rm -rf /var/lib/apt/lists/*

COPY uv /usr/local/bin/uv
COPY uvx /usr/local/bin/uvx
RUN chmod +x /usr/local/bin/uv /usr/local/bin/uvx

# Install dependencies system-wide to avoid networking issues during test runs
RUN uv pip install --system pytest==8.4.1 pytest-json-ctrf==0.3.5

WORKDIR /app

COPY merkle_log.py /app/merkle_log.py

# Seed the SQLite audit database
RUN python3 -c 'import sqlite3; \
    entries = ["user=alice action=login ts=1700000001", "user=bob action=read_file item=etc_config ts=1700000042", "user=alice action=write_file item=app_data_csv ts=1700000093", "user=carol action=login ts=1700000150", "user=bob action=logout ts=1700000201", "user=alice action=delete_file item=tmp_old_log ts=1700000312", "user=carol action=read_file item=app_data_csv ts=1700000401", "user=admin action=config_change key=timeout val=30 ts=1700000512"]; \
    conn = sqlite3.connect("/app/audit.db"); \
    conn.execute("CREATE TABLE audit_log (id INTEGER PRIMARY KEY, entry TEXT NOT NULL)"); \
    conn.executemany("INSERT INTO audit_log (entry) VALUES (?)", [(e,) for e in entries]); \
    conn.commit(); \
    conn.close(); \
    print("Seeded audit.db with", len(entries), "entries")'
