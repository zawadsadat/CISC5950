#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from collections import defaultdict

def emit_vehicle(vehicle_key, total_count, color_counts):
    if vehicle_key is None:
        return

    dominant_color = ""
    if color_counts:
        dominant_color = sorted(
            color_counts.items(),
            key=lambda kv: (-kv[1], kv[0])
        )[0][0]

    print(f"{vehicle_key}\t{dominant_color}\t{total_count}")

def main() -> int:
    current_vehicle = None
    total_count = 0
    color_counts = defaultdict(int)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        parts = line.split("\t", 1)
        if len(parts) != 2:
            continue

        vehicle_key, color = parts
        color = color.strip()

        if vehicle_key == current_vehicle:
            total_count += 1
            if color:
                color_counts[color] += 1
        else:
            emit_vehicle(current_vehicle, total_count, color_counts)
            current_vehicle = vehicle_key
            total_count = 1
            color_counts = defaultdict(int)
            if color:
                color_counts[color] += 1

    emit_vehicle(current_vehicle, total_count, color_counts)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())