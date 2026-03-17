FROM python:3.13-slim

RUN apt-get update && apt-get install -y tmux && rm -rf /var/lib/apt/lists/*

COPY uv /usr/local/bin/uv
COPY uvx /usr/local/bin/uvx
RUN chmod +x /usr/local/bin/uv /usr/local/bin/uvx

RUN uvx -p 3.13 -w pytest==8.4.1 -w pytest-json-ctrf==0.3.5 pytest --version

RUN pip install --break-system-packages rapidfuzz==3.10.1

WORKDIR /app

# Generate dataset, keep ground_truth.json accessible to tests but not in plain sight
COPY generate_data.py /app/generate_data.py
RUN python3 /app/generate_data.py && rm /app/generate_data.py
# Move ground truth out of /app so agent can't trivially read it
RUN mv /app/ground_truth.json /ground_truth.json
