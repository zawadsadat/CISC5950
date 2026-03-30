#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys


def main() -> int:
    # Accumulate per-cluster data
    cluster_data = {}  

    current_cluster = None
    user_count = 0
    sums = [0.0, 0.0, 0.0]

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        parts = line.split("\t", 1)
        if len(parts) != 2:
            continue

        cluster_id = parts[0]
        values = parts[1].split(",")

        if len(values) != 4:
            continue

        try:
            features = [float(x) for x in values[1:4]]
        except Exception:
            continue

        if cluster_id == current_cluster:
            user_count += 1
            sums = [s + f for s, f in zip(sums, features)]
        else:
            if current_cluster is not None:
                cluster_data[current_cluster] = (user_count, sums[:])
            current_cluster = cluster_id
            user_count = 1
            sums = features[:]

    if current_cluster is not None:
        cluster_data[current_cluster] = (user_count, sums[:])

    if not cluster_data:
        return 0

    # Compute means per cluster
    cluster_profiles = []
    total_users = sum(v[0] for v in cluster_data.values())

    for cid, (ucount, raw_sums) in sorted(cluster_data.items()):
        means = [s / ucount for s in raw_sums]
        cluster_profiles.append((cid, ucount, means))

    # Rank-based segment assignment:
    # Score = R + F + M  (lower recency is better, higher frequency and monetary are better)
    # Highest score = Champions, then Potential Loyalists, At Risk, New/Casual
    scored = []
    for cid, ucount, means in cluster_profiles:
        r, f, m = means
        score = -r + f + m  # combined RFM score
        scored.append((score, cid, ucount, means))

    scored.sort(key=lambda x: -x[0])  # best first

    SEGMENT_ORDER = [
        ("Champions", "VIP programs, loyalty rewards"),
        ("Potential Loyalists", "Personalized recommendations, upgrade incentives"),
        ("At Risk", "Win-back campaigns, special offers"),
        ("New/Casual", "Welcome series, educational content"),
    ]

    print("Cluster\tUsers\tPct_Users\tAvg_R\tAvg_F\tAvg_M\tSegment\tStrategy")

    for i, (score, cid, ucount, means) in enumerate(scored):
        r, f, m = means
        pct = (ucount / total_users * 100.0) if total_users else 0.0
        segment, strategy = SEGMENT_ORDER[min(i, len(SEGMENT_ORDER) - 1)]

        print(
            f"Cluster {cid}\t{ucount}\t{pct:.1f}%\t"
            f"R={r:.4f}\tF={f:.4f}\tM={m:.4f}\t"
            f"{segment}\t{strategy}"
        )

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
