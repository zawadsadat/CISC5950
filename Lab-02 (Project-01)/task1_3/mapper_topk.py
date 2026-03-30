#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import csv
from collections import defaultdict

TOP_K = 20

def main() -> int:
    reader = csv.reader(sys.stdin)
    counts = defaultdict(int)

    for row in reader:
        if not row:
            continue

        # cleaned dataset = original 43 cols + appended hour_of_day = 44 cols
        if len(row) < 25:
            continue

        # skip accidental header
        if row[0].strip() == "summons_number":
            continue

        street_code = row[9].strip()
        street_name = row[24].strip()

        if street_code == "" and street_name == "":
            continue

        location_key = f"{street_code}|{street_name}"
        counts[location_key] += 1

    topk = sorted(counts.items(), key=lambda x: (-x[1], x[0]))[:TOP_K]

    for location_key, cnt in topk:
        print(f"{location_key}\t{cnt}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())