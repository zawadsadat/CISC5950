#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

def main() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) != 6:
            continue

        hour, ip, req, err, sens, score = parts

        # Key is ALL so we compute top-3 across entire range (not per hour)
        print(f"ALL\t{score}\t{hour}\t{ip}\t{req}\t{err}\t{sens}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
