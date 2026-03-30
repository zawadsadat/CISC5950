#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from collections import defaultdict

TOP_K = 20
AVG_FINE = 65  # assumed average fine for Task 1.3

def main() -> int:
    global_counts = defaultdict(int)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) != 2:
            continue

        location_key, cnt_s = parts
        try:
            cnt = int(cnt_s)
        except ValueError:
            continue

        global_counts[location_key] += cnt

    top20 = sorted(global_counts.items(), key=lambda x: (-x[1], x[0]))[:TOP_K]

    print("Rank\tStreet_Code\tStreet_Name\tTickets\tEst_Revenue")

    rank = 1
    for location_key, tickets in top20:
        if "|" in location_key:
            street_code, street_name = location_key.split("|", 1)
        else:
            street_code, street_name = "", location_key

        est_revenue = tickets * AVG_FINE
        print(f"{rank}\t{street_code}\t{street_name}\t{tickets}\t{est_revenue}")
        rank += 1

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
