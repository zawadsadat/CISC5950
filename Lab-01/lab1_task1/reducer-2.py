#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

def emit_top3(hour: str, items: list[tuple[int, str, str, str, str]]) -> None:
    # Sort by score desc, then IP asc for deterministic ties
    items.sort(key=lambda x: (-x[0], x[1]))
    for score, ip, req, err, sens in items[:3]:
        print(f"{hour}\t{ip}\t{score}\t{req}\t{err}\t{sens}")

def main() -> int:
    current_hour = None
    bucket: list[tuple[int, str, str, str, str]] = []

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) != 6:
            continue

        hour, score_s, ip, req, err, sens = parts
        try:
            score = int(score_s)
        except ValueError:
            continue

        if hour == current_hour:
            bucket.append((score, ip, req, err, sens))
        else:
            if current_hour is not None:
                emit_top3(current_hour, bucket)
            current_hour = hour
            bucket = [(score, ip, req, err, sens)]

    if current_hour is not None:
        emit_top3(current_hour, bucket)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
