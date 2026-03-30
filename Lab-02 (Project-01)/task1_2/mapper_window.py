#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

def main() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) != 2:
            continue

        hour, count = parts

        # Skip header line if present
        if hour == "Hour":
            continue

        print(f"ALL\t{hour}\t{count}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
