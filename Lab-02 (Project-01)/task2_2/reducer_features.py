#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from datetime import datetime, timedelta

TIME_FMT = "%Y-%m-%d %H:%M:%S"

# Normalization constants
R_NORM = 90.0
F_NORM = 50.0
M_NORM = 5000.0


def main() -> int:
    # First pass: collect all user data
    users = {}
    global_max_time = None

    current_user = None
    sessions = 0
    max_end_time = None
    total_revenue = 0.0

    def flush_user():
        nonlocal global_max_time
        if current_user is None:
            return
        users[current_user] = (sessions, max_end_time, total_revenue)
        if global_max_time is None or max_end_time > global_max_time:
            global_max_time = max_end_time

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) != 4:
            continue

        user_id = parts[0]

        try:
            end_time = datetime.strptime(parts[1], TIME_FMT)
            converted = int(parts[2])
            revenue = float(parts[3])
        except Exception:
            continue

        if user_id == current_user:
            sessions += 1
            if end_time > max_end_time:
                max_end_time = end_time
            total_revenue += revenue
        else:
            flush_user()
            current_user = user_id
            sessions = 1
            max_end_time = end_time
            total_revenue = revenue

    flush_user()

    # Reference date = 1 day after the latest activity in the dataset
    if global_max_time is None:
        return 0
    reference_date = global_max_time + timedelta(days=1)

    # Output normalized RFM features
    for user_id in sorted(users.keys()):
        sess, max_et, tot_rev = users[user_id]

        days_since = (reference_date - max_et).total_seconds() / 86400.0
        if days_since < 0:
            days_since = 0.0

        r = min(days_since / R_NORM, 1.0)
        f = min(sess / F_NORM, 1.0)
        m = min(tot_rev / M_NORM, 1.0)

        print(f"{user_id},{r:.6f},{f:.6f},{m:.6f}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
