#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import csv

#normalization helpers

COLOR_MAP = {
    "BLK": "BLACK", "BLACK": "BLACK", "BK": "BLACK",
    "BL": "BLUE", "BLU": "BLUE", "BLUE": "BLUE", "BLW": "BLUE",
    "WH": "WHITE", "WHT": "WHITE", "WHITE": "WHITE", "WT": "WHITE", "WHI": "WHITE",
    "GRY": "GRAY", "GRAY": "GRAY", "GREY": "GRAY", "GY": "GRAY", "GR": "GRAY",
    "LTGY": "GRAY", "GRGY": "GRAY",
    "RED": "RED", "RD": "RED", "R": "RED",
    "GREEN": "GREEN", "GRN": "GREEN", "GN": "GREEN", "GL": "GREEN",
    "SILVER": "SILVER", "SIL": "SILVER", "SLV": "SILVER", "SILV": "SILVER", "SILVE": "SILVER",
    "BROWN": "BROWN", "BRN": "BROWN", "BR": "BROWN",
    "TAN": "TAN", "TN": "TAN",
    "YELLOW": "YELLOW", "YL": "YELLOW", "YEL": "YELLOW", "YELL": "YELLOW", "YW": "YELLOW",
    "BEIGE": "BEIGE", "BG": "BEIGE",
    "ORANGE": "ORANGE", "ORG": "ORANGE", "ORANG": "ORANGE", "OR": "ORANGE",
    "PURPLE": "PURPLE", "PR": "PURPLE",
    "MAROON": "MAROON", "MR": "MAROON",
    "GOLD": "GOLD", "GLD": "GOLD",
    "PINK": "PINK", "PK": "PINK",
    "YELLO": "YELLOW", "BLGY": "GRAY", "DKGY": "GRAY",
    "DKG": "GREEN", "LTBR": "BROWN", "WHBK": "WHITE", "BKWH": "BLACK",
    "OTHER": "OTHER",
    "UNKNOWN": "UNKNOWN", "UNK": "UNKNOWN", "UNKNO": "UNKNOWN",
}

STATE_MAP = {
    "NY": "NY", "NEW YORK": "NY", "N Y": "NY",
    "NJ": "NJ", "NEW JERSEY": "NJ",
    "PA": "PA", "PENNSYLVANIA": "PA",
    "CT": "CT", "CONNECTICUT": "CT",
    "MA": "MA", "MASSACHUSETTS": "MA",
    "FL": "FL", "FLORIDA": "FL",
    "CA": "CA", "CALIFORNIA": "CA",
    "TX": "TX", "TEXAS": "TX",
    "VA": "VA", "VIRGINIA": "VA",
    "MD": "MD", "MARYLAND": "MD",
    "DC": "DC", "DISTRICT OF COLUMBIA": "DC",
    "DE": "DE", "DELAWARE": "DE",
    "RI": "RI", "RHODE ISLAND": "RI",
    "NH": "NH", "NEW HAMPSHIRE": "NH",
    "VT": "VT", "VERMONT": "VT",
    "ME": "ME", "MAINE": "ME",
    "NC": "NC", "NORTH CAROLINA": "NC",
    "SC": "SC", "SOUTH CAROLINA": "SC",
    "GA": "GA", "GEORGIA": "GA",
    "OH": "OH", "OHIO": "OH",
    "IL": "IL", "ILLINOIS": "IL",
    "MI": "MI", "MICHIGAN": "MI",
    "WA": "WA", "WASHINGTON": "WA",
    "AZ": "AZ", "ARIZONA": "AZ",
    "CO": "CO", "COLORADO": "CO",
}

# Known column positions (same for both header formats)
POS = {
    "plate_id": 1,
    "registration_state": 2,
    "issue_date": 4,
    "violation_code": 5,
    "violation_time": 19,
    "vehicle_color": 33,
}

HEADER_ALIASES = {
    "summons_number": "summons_number", "summons number": "summons_number",
    "plate_id": "plate_id", "plate id": "plate_id",
    "registration_state": "registration_state", "registration state": "registration_state",
    "issue_date": "issue_date", "issue date": "issue_date",
    "violation_code": "violation_code", "violation code": "violation_code",
    "vehicle_color": "vehicle_color", "vehicle color": "vehicle_color",
    "violation_time": "violation_time", "violation time": "violation_time",
}


def clean_text(s: str) -> str:
    return (s or "").strip()


def normalize_color(color: str) -> str:
    raw = clean_text(color).upper()
    if not raw:
        return ""
    return COLOR_MAP.get(raw, raw)


def normalize_state(state: str) -> str:
    raw = clean_text(state).upper()
    if not raw:
        return ""
    return STATE_MAP.get(raw, raw)


def valid_issue_date(issue_date: str) -> bool:
    s = clean_text(issue_date)
    if len(s) < 8:
        return False
    if len(s) >= 4 and s[4:5] == "-":
        year = s[:4]
    elif "/" in s:
        parts = s.split("/")
        if len(parts) >= 3:
            year = parts[2][:4]
        else:
            return False
    else:
        year = s[:4]
    return year in ("2024", "2025")


def extract_hour(violation_time: str) -> str:
    s = clean_text(violation_time).upper()
    if len(s) < 5:
        return ""
    time_part = s[:4]
    ampm = s[-1]
    if not time_part.isdigit() or ampm not in ("A", "P"):
        return ""
    hh = int(time_part[:2])
    mm = int(time_part[2:4])
    if hh < 1 or hh > 12 or mm < 0 or mm > 59:
        return ""
    if ampm == "A":
        if hh == 12:
            hh = 0
    else:
        if hh != 12:
            hh += 12
    return str(hh)


def escape_csv_field(field: str) -> str:
    if "," in field or '"' in field or "\n" in field:
        return '"' + field.replace('"', '""') + '"'
    return field


def is_header_row(row):
    """Check if a row is a header line (either format)."""
    first = row[0].strip().lower()
    return first in ("summons_number", "summons number")


def build_index(header):
    """Build column index from header. Returns None if header not recognized."""
    idx = {}
    matched = 0
    for i, name in enumerate(header):
        canonical = HEADER_ALIASES.get(name.strip().lower())
        if canonical:
            idx[canonical] = i
            matched += 1
    if matched >= 3:
        return idx
    return None


def main() -> int:
    reader = csv.reader(sys.stdin)

    idx = None
    header_len = 43  # n of columns

    for row in reader:
        if not row:
            continue

        # Try to detect and skip header rows
        if is_header_row(row):
            result = build_index(row)
            if result:
                idx = result
                header_len = len(row)
            continue

        # If we never saw a header, use positional indexing
        if idx is None:
            idx = dict(POS)

        if len(row) < max(idx.values()) + 1:
            row += [""] * (max(idx.values()) + 1 - len(row))

        try:
            plate_id = clean_text(row[idx["plate_id"]])
            violation_code = clean_text(row[idx["violation_code"]])
            issue_date = clean_text(row[idx["issue_date"]])
        except (KeyError, IndexError):
            continue

        if not plate_id or not violation_code or not issue_date:
            continue

        if not valid_issue_date(issue_date):
            continue

        row[idx["registration_state"]] = normalize_state(row[idx["registration_state"]])
        row[idx["vehicle_color"]] = normalize_color(row[idx["vehicle_color"]])

        hour_of_day = extract_hour(row[idx["violation_time"]])

        line = ",".join(escape_csv_field(f) for f in row + [hour_of_day])
        print(line)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
