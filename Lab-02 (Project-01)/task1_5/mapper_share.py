#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

def main() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) != 5:
            continue

        code, label, fine, tickets, revenue = parts
        print(f"ALL\t{code}\t{label}\t{fine}\t{tickets}\t{revenue}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())