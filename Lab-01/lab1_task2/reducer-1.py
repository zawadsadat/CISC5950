#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

def main() -> int:
    current_key = None
    req_sum = err_sum = sens_sum = 0

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) != 4:
            continue

        key, req_s, err_s, sens_s = parts
        try:
            req = int(req_s)
            err = int(err_s)
            sens = int(sens_s)
        except ValueError:
            continue

        if key == current_key:
            req_sum += req
            err_sum += err
            sens_sum += sens
        else:
            if current_key is not None:
                score = req_sum + 3 * err_sum + 10 * sens_sum
                hour, ip = current_key.split("|", 1)
                print(f"{hour}\t{ip}\t{req_sum}\t{err_sum}\t{sens_sum}\t{score}")

            current_key = key
            req_sum, err_sum, sens_sum = req, err, sens

    if current_key is not None:
        score = req_sum + 3 * err_sum + 10 * sens_sum
        hour, ip = current_key.split("|", 1)
        print(f"{hour}\t{ip}\t{req_sum}\t{err_sum}\t{sens_sum}\t{score}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
