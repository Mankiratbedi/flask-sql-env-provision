#!/usr/bin/env python3
"""Generate deterministic SSH auth.log for ssh-log-analyzer task.

Log statistics:
- Total failed attempts: 50,000
- Total successful logins: 300
- Top attacked user: root (40,600)
- Top attacking IP: 203.0.113.1 (5,000)
- Peak attack hour: 02 (26,600 events)
- Brute force IPs (>500 failed): 39
"""

lines = []
pid = 10000


def add_failed(day, hour, user, ip, count):
    global pid
    for i in range(count):
        pid += 1
        minute = i % 60
        second = (i // 60) % 60
        port = 10000 + (pid % 55000)
        ts = f"Jan {day:2d} {hour:02d}:{minute:02d}:{second:02d}"
        lines.append(
            f"{ts} server01 sshd[{pid}]: Failed password for {user} from {ip} port {port} ssh2"
        )


def add_success(day, hour, user, ip, count):
    global pid
    for i in range(count):
        pid += 1
        minute = i % 60
        second = (i // 60) % 60
        port = 20000 + (pid % 45000)
        ts = f"Jan {day:2d} {hour:02d}:{minute:02d}:{second:02d}"
        lines.append(
            f"{ts} server01 sshd[{pid}]: Accepted password for {user} from {ip} port {port} ssh2"
        )


# === HEAVY ATTACKERS ===
# 203.0.113.1: 5,000 total (all root, hour 02)
add_failed(1, 2, "root", "203.0.113.1", 5000)

# 203.0.113.2: 4,000 total (root hour 02, admin hour 03)
add_failed(2, 2, "root", "203.0.113.2", 3000)
add_failed(2, 3, "admin", "203.0.113.2", 1000)

# 203.0.113.3: 3,000 total (root hour 02, admin+mysql hour 03)
add_failed(3, 2, "root", "203.0.113.3", 2000)
add_failed(3, 3, "admin", "203.0.113.3", 800)
add_failed(3, 3, "mysql", "203.0.113.3", 200)

# 203.0.113.4: 2,000 total (root hour 02, admin+mysql hour 04)
add_failed(4, 2, "root", "203.0.113.4", 1200)
add_failed(4, 4, "admin", "203.0.113.4", 500)
add_failed(4, 4, "mysql", "203.0.113.4", 300)

# 203.0.113.5: 1,500 total (root hour 02, admin+oracle hour 05)
add_failed(5, 2, "root", "203.0.113.5", 900)
add_failed(5, 5, "admin", "203.0.113.5", 300)
add_failed(5, 5, "oracle", "203.0.113.5", 300)

# === MEDIUM ATTACKERS ===
# 20 IPs, each 700 root + 300 admin = 1,000 total per IP = 20,000 total
for idx in range(1, 21):
    ip = f"198.51.100.{idx}"
    day = (idx % 28) + 1
    hour = 6 + (idx % 10)
    add_failed(day, hour, "root", ip, 700)
    add_failed(day, hour, "admin", ip, 300)

# === LIGHT ATTACKERS ===
# 14 IPs with 1,000 each + 1 IP with 500 = 14,500 total (all root, hour 02)
for idx in range(1, 16):
    ip = f"10.20.30.{idx}"
    day = (idx % 28) + 1
    count = 1000 if idx < 15 else 500
    add_failed(day, 2, "root", ip, count)

# === SUCCESSFUL LOGINS ===
add_success(10, 9, "alice", "10.0.0.10", 100)
add_success(11, 10, "bob", "10.0.0.11", 80)
add_success(12, 9, "charlie", "10.0.0.12", 60)
add_success(13, 11, "diana", "10.0.0.13", 40)
add_success(14, 14, "eve", "10.0.0.14", 20)

for line in lines:
    print(line)
