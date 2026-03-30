#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Session schema (13 cols):
  0  session_id
  1  user_id
  2  start_time
  3  end_time
  4  duration_minutes
  5  event_count
  6  converted
  7  total_revenue
  8  device_type
  9  traffic_source
  10 has_view
  11 has_cart
  12 has_purchase
"""

import sys
import csv

def main() -> int:
    reader = csv.reader(sys.stdin)

    for row in reader:
        if not row:
            continue

        if len(row) < 13:
            continue

        # Skip header lines (from multi-reducer output)
        if row[0].strip() == "session_id":
            continue

        # Skip summary metric lines
        if row[0].strip().startswith("==="):
            continue

        user_id = row[1].strip()
        end_time = row[3].strip()       # latest activity timestamp
        converted = row[6].strip()       # 1 or 0
        revenue = row[7].strip()         # purchase revenue

        if not user_id or not end_time:
            continue

        try:
            float(revenue)
            int(converted)
        except Exception:
            continue

        
        print(f"{user_id}\t{end_time}\t{converted}\t{revenue}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
