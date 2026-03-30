#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

EXPECTED_KEYS = [
    "TOTAL_INPUT",
    "VALID_OUTPUT_RECORDS",
    "INVALID_DATE_RECORDS",
    "MISSING_CRITICAL_FIELDS",
    "COLOR_STANDARDIZATIONS",
    "STATE_CODE_CORRECTIONS",
]

def main() -> int:
    counters = {k: 0 for k in EXPECTED_KEYS}

    current_key = None
    current_sum = 0

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) != 2:
            continue

        key, value_s = parts
        try:
            value = int(value_s)
        except ValueError:
            continue

        if key == current_key:
            current_sum += value
        else:
            if current_key is not None:
                counters[current_key] = counters.get(current_key, 0) + current_sum
            current_key = key
            current_sum = value

    # Flush last key
    if current_key is not None:
        counters[current_key] = counters.get(current_key, 0) + current_sum

    # Print report with percentages
    total = counters.get("TOTAL_INPUT", 0)

    for key in EXPECTED_KEYS:
        val = counters[key]
        if total > 0 and key != "TOTAL_INPUT":
            pct = val / total * 100
            print(f"{key}\t{val}\t({pct:.1f}%)")
        else:
            print(f"{key}\t{val}")

    # Print any unexpected counters that weren't in EXPECTED_KEYS
    for key in sorted(counters.keys()):
        if key not in EXPECTED_KEYS:
            val = counters[key]
            if total > 0:
                pct = val / total * 100
                print(f"{key}\t{val}\t({pct:.1f}%)")
            else:
                print(f"{key}\t{val}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
