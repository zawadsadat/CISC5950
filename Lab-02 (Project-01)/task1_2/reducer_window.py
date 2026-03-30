#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

def main() -> int:
    hourly = {h: 0 for h in range(24)}

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) != 3:
            continue

        key, hour_s, count_s = parts
        if key != "ALL":
            continue

        try:
            hour = int(hour_s)
            count = int(count_s)
        except ValueError:
            continue

        if 0 <= hour <= 23:
            hourly[hour] += count

    best_start = 0
    best_total = -1

    for start in range(24):
        total = 0
        for offset in range(4):
            h = (start + offset) % 24
            total += hourly[h]

        if total > best_total:
            best_total = total
            best_start = start

    best_end = (best_start + 3) % 24

    print(f"Start_Hour\tEnd_Hour\tTotal_Tickets")
    print(f"{best_start}\t{best_end}\t{best_total}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
