FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    asciinema \
    ca-certificates \
    tmux \
    curl \
    sqlite3 \
    procps \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Pre-cache app dependencies offline into /opt/wheels so agent can install them offline.
RUN mkdir -p /opt/wheels \
 && pip download --dest /opt/wheels \
    flask==3.0.3 \
    Flask-SQLAlchemy==3.1.1 \
    cryptography==43.0.1 \
    requests==2.32.3

# Set up isolated verifier virtual environment at build time.
# Test-only deps must be kept out of the system environment.
RUN python3 -m venv /opt/verifier-venv \
 && /opt/verifier-venv/bin/pip install --no-cache-dir \
    pytest==8.4.1 \
    pytest-json-ctrf==0.3.5 \
    ruff==0.6.9

WORKDIR /app

COPY api/ /app/api/
COPY provision.py /app/
RUN chmod +x /app/provision.py
