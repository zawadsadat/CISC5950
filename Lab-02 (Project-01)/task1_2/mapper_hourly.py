#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import csv

def main() -> int:
    reader = csv.reader(sys.stdin)

    for row in reader:
        if not row:
            continue

        # cleaned data has hour_of_day as the last column
        hour = row[-1].strip()

        if hour == "hour_of_day" or hour == "":
            continue

        try:
            h = int(hour)
        except ValueError:
            continue

        if 0 <= h <= 23:
            print(f"{h}\t1")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())