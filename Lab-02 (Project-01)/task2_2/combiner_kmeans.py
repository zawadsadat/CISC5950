#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

def emit(cluster_id, count, sums):
    if cluster_id is None:
        return
    print(
        f"{cluster_id}\t{count}\t"
        f"{sums[0]}\t{sums[1]}\t{sums[2]}"
    )

def main() -> int:
    current_cluster = None
    count = 0
    sums = [0.0, 0.0, 0.0]

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) != 5:
            continue

        cluster_id = parts[0]
        try:
            c = int(parts[1])
            vals = [float(x) for x in parts[2:5]]
        except Exception:
            continue

        if cluster_id == current_cluster:
            count += c
            sums = [s + v for s, v in zip(sums, vals)]
        else:
            emit(current_cluster, count, sums)
            current_cluster = cluster_id
            count = c
            sums = vals

    emit(current_cluster, count, sums)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
