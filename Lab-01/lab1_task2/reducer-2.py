#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

def main() -> int:
    items = []  # (score_int, hour, ip, req, err, sens)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) != 7:
            continue

        key, score_s, hour, ip, req, err, sens = parts
        if key != "ALL":
            continue

        try:
            score = int(score_s)
        except ValueError:
            continue

        items.append((score, hour, ip, req, err, sens))

    # Sort descending by score, then hour asc, then ip asc
    items.sort(key=lambda x: (-x[0], x[1], x[2]))

    # Final output
    # hour ip score req err sens
    for score, hour, ip, req, err, sens in items[:3]:
        print(f"{hour}\t{ip}\t{score}\t{req}\t{err}\t{sens}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
