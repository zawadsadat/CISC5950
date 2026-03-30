#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Input schema (10 columns):
  0  event_id
  1  user_id
  2  timestamp
  3  session_id
  4  event_type
  5  product_id
  6  category
  7  price
  8  device_type
  9  traffic_source
"""

import sys
import csv
from datetime import datetime

# Supported timestamp formats in the data
TS_FORMATS = [
    "%Y-%m-%d %H:%M:%S",  # 2025-12-04 23:22:55
    "%Y-%m-%dT%H:%M:%S",  # 2025-12-04T23:22:55
    "%m/%d/%Y %H:%M:%S",  # 12/4/2025 23:22:55
    "%m/%d/%Y %H:%M",     # 12/4/2025 23:22
]

def parse_and_normalize_ts(raw_ts: str) -> str:
    """Parse timestamp in any supported format, return normalized YYYY-MM-DD HH:MM:SS."""
    raw_ts = raw_ts.strip()
    for fmt in TS_FORMATS:
        try:
            dt = datetime.strptime(raw_ts, fmt)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
    return ""


def main() -> int:

    lines = (line.replace("\r", "") for line in sys.stdin)
    first_line = next(lines, None)
    if first_line is None:
        return 0

    # Detect delimiter: if tab is present in first line, use tab; otherwise comma
    if "\t" in first_line:
        delimiter = "\t"
    else:
        delimiter = ","

    import itertools
    all_lines = itertools.chain([first_line], lines)
    reader = csv.reader(all_lines, delimiter=delimiter)

    for row in reader:
        if not row:
            continue

        if len(row) < 10:
            continue

        # Skip header
        if row[0].strip() == "event_id":
            continue

        event_id = row[0].strip()
        user_id = row[1].strip()
        raw_timestamp = row[2].strip()
        event_type = row[4].strip()
        price = row[7].strip()
        device_type = row[8].strip()
        traffic_source = row[9].strip()

        if not user_id or not raw_timestamp:
            continue

        # Normalize timestamp to sortable format
        timestamp = parse_and_normalize_ts(raw_timestamp)
        if not timestamp:
            continue

        print(
            f"{user_id}\t{timestamp}\t{event_id}\t{event_type}\t{price}\t{device_type}\t{traffic_source}"
        )

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
