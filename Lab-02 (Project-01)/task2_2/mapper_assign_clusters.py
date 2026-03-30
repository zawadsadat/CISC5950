#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import math
import csv

CENTROID_FILE = "centroids.txt"

def load_centroids():
    centroids = []
    with open(CENTROID_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or len(row) < 4:
                continue
            cid = row[0].strip()
            try:
                vals = [float(x) for x in row[1:4]]
            except Exception:
                continue
            centroids.append((cid, vals))
    return centroids

def euclidean(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

def main() -> int:
    centroids = load_centroids()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        parts = line.split(",")
        if len(parts) != 4:
            continue

        user_id = parts[0].strip()

        try:
            features = [float(x) for x in parts[1:4]]
        except Exception:
            continue

        best_cluster = None
        best_dist = float("inf")

        for cid, center in centroids:
            d = euclidean(features, center)
            if d < best_dist:
                best_dist = d
                best_cluster = cid

        if best_cluster is not None:
            print(f"{best_cluster}\t{user_id},{','.join(parts[1:4])}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
