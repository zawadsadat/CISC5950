#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

def emit_record(current_key, ticket_sum, revenue_sum):
    if current_key is None:
        return

    code, label, fine = current_key.split("|", 2)
    print(f"{code}\t{label}\t{fine}\t{ticket_sum}\t{revenue_sum}")

def main() -> int:
    current_key = None
    ticket_sum = 0
    revenue_sum = 0

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) != 3:
            continue

        key, tickets_s, revenue_s = parts

        try:
            tickets = int(tickets_s)
            revenue = int(revenue_s)
        except ValueError:
            continue

        if key == current_key:
            ticket_sum += tickets
            revenue_sum += revenue
        else:
            emit_record(current_key, ticket_sum, revenue_sum)
            current_key = key
            ticket_sum = tickets
            revenue_sum = revenue

    emit_record(current_key, ticket_sum, revenue_sum)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())