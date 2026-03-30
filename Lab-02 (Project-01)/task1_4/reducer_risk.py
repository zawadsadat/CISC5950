#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from collections import defaultdict

def main() -> int:
    color_ticket_totals = defaultdict(int)
    color_vehicle_counts = defaultdict(int)

    total_tickets_all = 0
    total_vehicles_all = 0

    bucket_5_10 = 0
    bucket_11_20 = 0
    bucket_21_plus = 0

    top_vehicle = ""
    top_vehicle_color = ""
    top_vehicle_count = -1

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) != 4:
            continue

        key, vehicle_key, color, count_s = parts
        if key != "ALL":
            continue

        try:
            count = int(count_s)
        except ValueError:
            continue

        total_tickets_all += count
        total_vehicles_all += 1

        color = color if color else "UNKNOWN"
        color_ticket_totals[color] += count
        color_vehicle_counts[color] += 1

        if 5 <= count <= 10:
            bucket_5_10 += 1
        elif 11 <= count <= 20:
            bucket_11_20 += 1
        elif count >= 21:
            bucket_21_plus += 1

        if count > top_vehicle_count:
            top_vehicle_count = count
            top_vehicle = vehicle_key
            top_vehicle_color = color

    overall_avg = 0.0
    if total_vehicles_all > 0:
        overall_avg = total_tickets_all / total_vehicles_all

    print("=== COLOR RISK ANALYSIS ===")
    print("Color\tTickets\tPct_Total\tRisk_Score")
    color_rows = []
    for color, tickets in color_ticket_totals.items():
        vehicles = color_vehicle_counts[color]
        pct_total = (tickets / total_tickets_all * 100.0) if total_tickets_all else 0.0
        avg_for_color = (tickets / vehicles) if vehicles else 0.0
        risk_score = (avg_for_color / overall_avg) if overall_avg else 0.0
        color_rows.append((color, tickets, pct_total, risk_score))

    color_rows.sort(key=lambda x: (-x[1], x[0]))

    for color, tickets, pct_total, risk_score in color_rows:
        print(f"{color}\t{tickets}\t{pct_total:.2f}%\t{risk_score:.2f}")

    print("=== REPEAT OFFENDER PATTERNS ===")
    print("Category\tVehicle_Count")
    print(f"5-10 violations\t{bucket_5_10}")
    print(f"11-20 violations\t{bucket_11_20}")
    print(f"21+ violations\t{bucket_21_plus}")

    print("=== TOP OFFENDER ===")
    print("Vehicle_Key\tColor\tTicket_Count")
    print(f"{top_vehicle}\t{top_vehicle_color}\t{top_vehicle_count}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
