#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

def main() -> int:
    current_hour = None
    current_sum = 0

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) != 2:
            continue

        hour, value_s = parts
        try:
            value = int(value_s)
        except ValueError:
            continue

        if hour == current_hour:
            current_sum += value
        else:
            if current_hour is not None:
                print(f"{current_hour}\t{current_sum}")
            current_hour = hour
            current_sum = value

    if current_hour is not None:
        print(f"{current_hour}\t{current_sum}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())