#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

def main() -> int:
    for line in sys.stdin:
        # Hadoop Streaming adds a tab between key and (empty) value.
        # Strip any trailing whitespace/tabs to produce clean CSV output.
        line = line.rstrip()
        if line:
            print(line)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
