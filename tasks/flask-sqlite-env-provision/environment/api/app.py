import hmac
import hashlib
import json
import os
import sqlite3
import time
from flask import Flask, jsonify, request, abort

app = Flask(__name__)

# Load configuration from the expected path
CONFIG_PATH = os.environ.get("FLASK_CONFIG_PATH", "/app/run/config.py")

if not os.path.exists(CONFIG_PATH):
    # Fallback to defaults or fail if path is missing
    app.config["SECRET_KEY"] = "temporary-dev-key-12345"
    app.config["DATABASE"] = "/app/run/assets.db"
else:
    # Safe load of custom config
    cfg = {}
    with open(CONFIG_PATH) as f:
        exec(f.read(), cfg)
    app.config["SECRET_KEY"] = cfg.get("SECRET_KEY", "fallback-key")
    app.config["DATABASE"] = cfg.get("DATABASE", "/app/run/assets.db")

def get_db():
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/health", methods=["GET"])
def health():
    # Verify DB connectivity as part of health check
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        cursor.close()
        conn.close()
        return jsonify({"status": "healthy", "database": "connected"})
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

def generate_admin_token(timestamp):
    # Generate an HMAC token for verification
    message = f"admin:{timestamp}".encode("utf-8")
    secret = app.config["SECRET_KEY"].encode("utf-8")
    return hmac.new(secret, message, hashlib.sha256).hexdigest()

def verify_token(token):
    # Verify the HMAC token against current time window (5-minute validity)
    if not token:
        return False
    current_time = int(time.time())
    for offset in range(-300, 300):
        t = current_time + offset
        if generate_admin_token(t) == token:
            return True
    return False

@app.route("/api/token", methods=["POST"])
def get_token():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    
    # Simple credentials for provisioning verification
    if username == "admin" and password == "secret-provision-password":
        current_time = int(time.time())
        token = generate_admin_token(current_time)
        return jsonify({"token": token, "expires_in": 300})
    
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/api/assets/<code_name>", methods=["GET"])
def get_asset(code_name):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM assets WHERE code = ?;", (code_name,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if row is None:
        return jsonify({"error": f"Asset {code_name} not found"}), 404
        
    return jsonify(dict(row))

@app.route("/api/assets", methods=["POST"])
def create_asset():
    auth_header = request.headers.get("Authorization", "")
    token = ""
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
    
    if not verify_token(token):
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.get_json() or {}
    code = data.get("code")
    name = data.get("name")
    quantity = data.get("quantity")
    
    if not code or not name or quantity is None:
        return jsonify({"error": "Missing required fields"}), 400
        
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO assets (code, name, quantity) VALUES (?, ?, ?);",
            (code, name, int(quantity))
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"status": "created", "code": code}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": f"Asset with code {code} already exists"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("FLASK_PORT", 5000))
    app.run(host="127.0.0.1", port=port)
