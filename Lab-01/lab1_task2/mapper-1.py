#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import re

# Matches lines like:

LOG_RE = re.compile(
    r'^(?P<ip>\d{1,3}(?:\.\d{1,3}){3})\s+.*?\[(?P<ts>[^\]]+)\]\s+'
    r'"(?P<method>[A-Z]+)\s+(?P<path>\S+)\s+[^"]+"\s+'
    r'"?(?P<status>\d{3})"?\s+'
)

# List from lab + 3 extras
SENSITIVE_PREFIXES = [
    "/admin",
    "/login",
    "/wp-login.php",
    "/.env",
    "/phpmyadmin",
    "/cgi-bin",
    "/user_login.php",
    # extras 
    "/.git",
    "/config",
    "/backup",
]

def extract_hour(ts: str):
    # Example: 05/Feb/2026:03:20:29 +0000  -> "03"
    try:
        after_date = ts.split(":", 1)[1]
        hour = after_date[:2]
        if hour.isdigit() and len(hour) == 2:
            return hour
    except Exception:
        pass
    return None

def is_sensitive(path: str) -> int:
    # ignore query params
    base = path.split("?", 1)[0]
    # prefix match so "/admin/xxx" counts too
    for p in SENSITIVE_PREFIXES:
        if base == p or base.startswith(p + "/"):
            return 1
    return 0

def parse_range(arg: str):
    if not arg or "-" not in arg:
        return None, None
    a, b = arg.split("-", 1)
    if len(a) != 2 or len(b) != 2 or (not a.isdigit()) or (not b.isdigit()):
        return None, None
    return int(a), int(b)

def in_range(hour_int: int, start: int, end: int) -> bool:
    if start is None or end is None:
        return True
    if start <= end:
        return start <= hour_int < end
    return (hour_int >= start) or (hour_int < end)

def main() -> int:
    rng = sys.argv[1] if len(sys.argv) > 1 else ""
    start, end = parse_range(rng)

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

        h = int(hour)
        if not in_range(h, start, end):
            continue

        req = 1
        err = 1 if (status.startswith("4") or status.startswith("5")) else 0
        sens = is_sensitive(path)

        # Composite key must be in FIRST field for Hadoop Streaming
        print(f"{hour}|{ip}\t{req}\t{err}\t{sens}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
