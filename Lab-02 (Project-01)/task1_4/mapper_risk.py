#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

def main() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) != 3:
            continue

        vehicle_key, color, ticket_count = parts
        print(f"ALL\t{vehicle_key}\t{color}\t{ticket_count}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())