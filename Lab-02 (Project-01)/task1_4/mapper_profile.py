#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import csv

def main() -> int:
    reader = csv.reader(sys.stdin)

    for row in reader:
        if not row:
            continue

        # cleaned dataset = original 43 columns + appended hour_of_day
        if len(row) < 44:
            continue

        # skip accidental header
        if row[0].strip() == "summons_number":
            continue

        plate_id = row[1].strip()
        reg_state = row[2].strip()
        plate_type = row[3].strip()
        vehicle_color = row[33].strip()

        if not plate_id:
            continue

        vehicle_key = f"{plate_id}|{reg_state}|{plate_type}"

        # value: color
        print(f"{vehicle_key}\t{vehicle_color}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())