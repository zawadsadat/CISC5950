#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import csv
import os

LOOKUP_FILE = "fine_lookup.csv"
DEFAULT_FINE = 50
DEFAULT_LABEL = "OTHER"

def load_lookup():
    lookup = {}

    if not os.path.exists(LOOKUP_FILE):
        return lookup

    with open(LOOKUP_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or len(row) < 3:
                continue

            code = row[0].strip()
            label = row[1].strip()

            # skip optional header
            if code.lower() == "violation_code":
                continue

            try:
                fine = int(row[2].strip())
            except ValueError:
                continue

            lookup[code] = (label, fine)

    return lookup

def main() -> int:
    lookup = load_lookup()
    reader = csv.reader(sys.stdin)

    for row in reader:
        if not row:
            continue

        # cleaned dataset = original 43 cols + appended hour_of_day
        if len(row) < 44:
            continue

        # skip header
        if row[0].strip() == "summons_number":
            continue

        violation_code = row[5].strip()
        if not violation_code:
            continue

        label, fine = lookup.get(violation_code, (DEFAULT_LABEL, DEFAULT_FINE))
        revenue = fine

        key = f"{violation_code}|{label}|{fine}"
        print(f"{key}\t1\t{revenue}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
