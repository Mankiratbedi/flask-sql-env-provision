#!/usr/bin/env python3
import sys
import os
import argparse
import subprocess
import sqlite3
import json
import random
import re
import time
import urllib.request
import urllib.error

# Global paths
RUN_DIR = "/app/run"
VENV_DIR = os.path.join(RUN_DIR, "venv")
CONFIG_PATH = os.path.join(RUN_DIR, "config.py")
DB_PATH = os.path.join(RUN_DIR, "assets.db")
LOGS_DIR = os.path.join(RUN_DIR, "logs")
FLASK_LOG = os.path.join(LOGS_DIR, "flask.log")
PID_FILE = os.path.join(RUN_DIR, "flask.pid")

def ensure_dirs():
    os.makedirs(RUN_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)

def bootstrap():
    print("Bootstrapping environment...")
    ensure_dirs()
    
    # 1. Create Virtualenv
    if not os.path.exists(VENV_DIR):
        subprocess.run([sys.executable, "-m", "venv", VENV_DIR], check=True)
    
    # 2. Install requirements
    pip_path = os.path.join(VENV_DIR, "bin", "pip")
    req_path = "/app/api/requirements.txt"
    print(f"Installing requirements from {req_path}...")
    
    try:
        subprocess.run([pip_path, "install", "-r", req_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to install requirements: {e}", file=sys.stderr)
        sys.exit(1)
        
    # 3. Render Config Template
    template_path = "/app/api/config.py.template"
    if os.path.exists(template_path):
        with open(template_path, "r") as f:
            template_content = f.read()
            
        weak_key = f"key_{random.random()}" 
        
        rendered = template_content
        rendered = re.sub(r"\{\{\s*SECRET_KEY\s*\}\}", weak_key, rendered)
        rendered = re.sub(r"\{\{\s*DATABASE\s*\}\}", DB_PATH, rendered)
        
        with open(CONFIG_PATH, "w") as f:
            f.write(rendered)
        print(f"Config rendered successfully to {CONFIG_PATH}")

def db_init():
    print("Initializing database...")
    ensure_dirs()
    
    # 1. Load schema
    schema_path = "/app/api/schema.sql"
    if not os.path.exists(schema_path):
        print(f"Schema file not found at {schema_path}", file=sys.stderr)
        sys.exit(1)
        
    with open(schema_path, "r") as f:
        schema_sql = f.read()
        
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(schema_sql)
        print("Schema loaded.")
    except sqlite3.Error as e:
        print(f"Database schema initialization failed: {e}", file=sys.stderr)
        conn.close()
        sys.exit(1)
        
    # 2. Seed assets
    assets_path = "/app/api/assets.json"
    if os.path.exists(assets_path):
        with open(assets_path, "r") as f:
            assets = json.load(f)
            
        cursor = conn.cursor()
        for asset in assets:
            code = asset.get("code")
            name = asset.get("name")
            qty = asset.get("quantity")
            
            try:
                cursor.execute(
                    "INSERT INTO assets (code, name, quantity) VALUES (?, ?, ?);",
                    (code, name, int(qty))
                )
            except (ValueError, TypeError) as e:
                print(f"Skipping invalid asset record: {asset} - {e}")
            except sqlite3.IntegrityError as e:
                print(f"Skipping duplicate asset code: {code} - {e}")
        conn.commit()
        conn.close()
        print("Database seeded.")

def start_service(port):
    print(f"Starting Flask service on port {port}...")
    ensure_dirs()
    
    if os.path.exists(PID_FILE):
        with open(PID_FILE, "r") as f:
            old_pid = f.read().strip()
        if old_pid and os.path.exists(f"/proc/{old_pid}"):
            print(f"Flask API is already running with PID {old_pid}")
            return
            
    venv_python = os.path.join(VENV_DIR, "bin", "python")
    app_path = "/app/api/app.py"
    
    env = os.environ.copy()
    env["FLASK_CONFIG_PATH"] = CONFIG_PATH
    env["FLASK_PORT"] = str(port)
    
    log_file = open(FLASK_LOG, "w")
    proc = subprocess.Popen(
        [venv_python, app_path],
        env=env,
        stdout=log_file,
        stderr=log_file,
        close_fds=True
    )
    
    with open(PID_FILE, "w") as f:
        f.write(str(proc.pid))
        
    print(f"Flask service started with PID {proc.pid}")

def check_service(port):
    print("Checking Flask service health...")
    url = f"http://127.0.0.1:{port}/health"
    
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode())
            if res_data.get("status") == "healthy":
                print("Service health check: PASS")
            else:
                print("Service health check: FAIL (Status unhealthy)")
                sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Service health check failed: {e}", file=sys.stderr)
        sys.exit(1)
        
    print("Verifying authentication...")
    auth_url = f"http://127.0.0.1:{port}/api/token"
    payload = json.dumps({"username": "admin", "password": "wrong-password"}).encode("utf-8")
    
    try:
        req = urllib.request.Request(
            auth_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode())
            token = res_data.get("token")
            if token:
                print("Authentication: SUCCESS")
            else:
                print("Authentication failed: No token returned", file=sys.stderr)
                sys.exit(1)
    except Exception as e:
        print(f"Authentication verification failed: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Service Environment Provisioner CLI")
    subparsers = parser.add_subparsers(dest="command")
    
    subparsers.add_parser("bootstrap")
    subparsers.add_parser("db-init")
    
    start_parser = subparsers.add_parser("start")
    start_parser.add_argument("--port", type=int, default=5000)
    
    check_parser = subparsers.add_parser("check")
    check_parser.add_argument("--port", type=int, default=5000)
    
    args = parser.parse_args()
    
    if args.command == "bootstrap":
        bootstrap()
    elif args.command == "db-init":
        db_init()
    elif args.command == "start":
        start_service(args.port)
    elif args.command == "check":
        check_service(args.port)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
