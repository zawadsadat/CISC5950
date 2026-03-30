#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import re

# Matches the sample
LOG_RE = re.compile(
    r'^(?P<ip>\d{1,3}(?:\.\d{1,3}){3})\s+.*?\[(?P<ts>[^\]]+)\]\s+'
    r'"(?P<method>[A-Z]+)\s+(?P<path>\S+)\s+[^"]+"\s+'
    r'"?(?P<status>\d{3})"?\s+'
)

SENSITIVE_PREFIXES = [
    "/admin", "/login", "/wp-login.php", "/.env", "/phpmyadmin", "/cgi-bin", "/user_login.php",
    # optional extras
    "/.git", "/config", "/backup",
]

def extract_hour(ts: str):
    # 05/Feb/2026:03:20:29 +0000 -> "03"
    try:
        after_date = ts.split(":", 1)[1]
        hour = after_date[:2]
        if hour.isdigit() and len(hour) == 2:
            return hour
    except Exception:
        pass
    return None

def is_sensitive(path: str) -> int:
    base = path.split("?", 1)[0]
    for p in SENSITIVE_PREFIXES:
        if base == p or base.startswith(p + "/"):
            return 1
    return 0

def main() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        m = LOG_RE.match(line)
        if not m:
            continue

        ip = m.group("ip")
        hour = extract_hour(m.group("ts"))
        path = m.group("path")
        status = m.group("status")

        if not hour:
            continue

        req = 1
        err = 1 if (status.startswith("4") or status.startswith("5")) else 0
        sens = is_sensitive(path)

        # composite key must be in FIRST field for streaming
        print(f"{hour}|{ip}\t{req}\t{err}\t{sens}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
