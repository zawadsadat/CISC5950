#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

def main() -> int:
    rows = []
    total_revenue_all = 0

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) != 6:
            continue

        key, code, label, fine_s, tickets_s, revenue_s = parts
        if key != "ALL":
            continue

        try:
            fine = int(fine_s)
            tickets = int(tickets_s)
            revenue = int(revenue_s)
        except ValueError:
            continue

        rows.append((code, label, fine, tickets, revenue))
        total_revenue_all += revenue

    rows.sort(key=lambda x: (-x[4], x[0]))

    rank = 1
    for code, label, fine, tickets, revenue in rows:
        pct = (revenue / total_revenue_all * 100.0) if total_revenue_all else 0.0
        print(f"{rank}\t{code}\t{label}\t{fine}\t{tickets}\t{revenue}\t{pct:.2f}%")
        rank += 1

    print(f"TOTAL_REVENUE\t{total_revenue_all}")

    if rows:
        best = rows[0]
        print(f"MOST_PROFITABLE\t{best[0]}\t{best[1]}\t{best[4]}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())