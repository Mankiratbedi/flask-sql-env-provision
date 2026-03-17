#!/usr/bin/env python3
"""Generate a realistic nginx access log for testing."""
import random

random.seed(42)

IPS = [f"192.168.{random.randint(1,5)}.{random.randint(1,254)}" for _ in range(50)]
METHODS = ["GET"] * 70 + ["POST"] * 20 + ["PUT"] * 7 + ["DELETE"] * 3
URLS = [
    "/api/users", "/api/orders", "/api/products", "/static/app.js",
    "/static/style.css", "/", "/login", "/logout", "/dashboard",
    "/api/users/123", "/api/orders/456", "/health", "/metrics",
    "/api/search", "/api/reports",
]
STATUSES = [200] * 60 + [201] * 10 + [301] * 5 + [304] * 5 + \
           [400] * 5 + [401] * 5 + [403] * 3 + [404] * 5 + [500] * 2

lines = []
# 800 requests on 15/Mar/2026
for i in range(800):
    ip = random.choice(IPS)
    method = random.choice(METHODS)
    url = random.choice(URLS)
    status = random.choice(STATUSES)
    size = random.randint(100, 50000)
    lines.append(
        f'{ip} - - [15/Mar/2026:{10 + i//200:02d}:{(i*7)%60:02d}:{(i*13)%60:02d} +0000] '
        f'"{method} {url} HTTP/1.1" {status} {size}'
    )
# 400 requests on 16/Mar/2026
for i in range(400):
    ip = random.choice(IPS)
    method = random.choice(METHODS)
    url = random.choice(URLS)
    status = random.choice(STATUSES)
    size = random.randint(100, 50000)
    lines.append(
        f'{ip} - - [16/Mar/2026:{8 + i//100:02d}:{(i*7)%60:02d}:{(i*13)%60:02d} +0000] '
        f'"{method} {url} HTTP/1.1" {status} {size}'
    )

random.shuffle(lines)
with open("/app/access.log", "w") as f:
    f.write("\n".join(lines) + "\n")
print(f"Generated {len(lines)} log lines to /app/access.log")
