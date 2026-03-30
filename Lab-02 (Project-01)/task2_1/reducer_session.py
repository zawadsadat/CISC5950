#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from datetime import datetime

TIME_FMT = "%Y-%m-%d %H:%M:%S"
SESSION_TIMEOUT_MINUTES = 30

def parse_ts(ts: str):
    return datetime.strptime(ts, TIME_FMT)

def safe_price(x: str) -> float:
    try:
        return float(x)
    except Exception:
        return 0.0

def format_session(
    user_id, session_index, start_ts, end_ts,
    event_count, has_view, has_cart, has_purchase,
    revenue, device_type, traffic_source
):
    if user_id is None or start_ts is None or end_ts is None:
        return None

    duration_minutes = int((end_ts - start_ts).total_seconds() // 60)
    session_id = f"{user_id}_R{session_index:03d}"

    line = (
        f"{session_id},"
        f"{user_id},"
        f"{start_ts.strftime(TIME_FMT)},"
        f"{end_ts.strftime(TIME_FMT)},"
        f"{duration_minutes},"
        f"{event_count},"
        f"{1 if has_purchase else 0},"
        f"{revenue:.2f},"
        f"{device_type},"
        f"{traffic_source},"
        f"{1 if has_view else 0},"
        f"{1 if has_cart else 0},"
        f"{1 if has_purchase else 0}"
    )
    return line, duration_minutes, event_count, has_purchase, revenue

def classify_event(event_type: str):
    et = (event_type or "").strip().lower()

    has_view = False
    has_cart = False
    has_purchase = False

    if et == "view":
        has_view = True
    elif et in ("cart", "add_to_cart", "addtocart"):
        has_cart = True
    elif et == "purchase":
        has_purchase = True

    return has_view, has_cart, has_purchase

def main() -> int:
    current_user = None
    session_index = 0

    session_start = None
    session_end = None
    last_ts = None
    event_count = 0
    has_view = False
    has_cart = False
    has_purchase = False
    revenue = 0.0
    session_device = ""
    session_source = ""

    # Summary accumulators
    total_sessions = 0
    total_duration = 0
    total_events = 0
    converted_sessions = 0
    converted_revenue = 0.0

    header_printed = False

    def output_session(uid, sidx, sstart, send, ecount, hview, hcart, hpurch, rev, dev, src):
        nonlocal header_printed, total_sessions, total_duration, total_events
        nonlocal converted_sessions, converted_revenue

        result = format_session(uid, sidx, sstart, send, ecount, hview, hcart, hpurch, rev, dev, src)
        if result is None:
            return

        line, dur, evts, was_converted, sess_rev = result

        if not header_printed:
            print("session_id,user_id,start_time,end_time,duration_minutes,"
                  "event_count,converted,total_revenue,device_type,traffic_source,"
                  "has_view,has_cart,has_purchase")
            header_printed = True

        print(line)

        total_sessions += 1
        total_duration += dur
        total_events += evts
        if was_converted:
            converted_sessions += 1
            converted_revenue += sess_rev

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) != 7:
            continue

        user_id, ts_s, event_id, event_type, price_s, device_type, traffic_source = parts

        try:
            ts = parse_ts(ts_s)
        except Exception:
            continue

        ev_view, ev_cart, ev_purchase = classify_event(event_type)

        # first session
        if current_user is None:
            current_user = user_id
            session_index = 1
            session_start = ts
            session_end = ts
            last_ts = ts
            event_count = 1
            has_view = ev_view
            has_cart = ev_cart
            has_purchase = ev_purchase
            revenue = safe_price(price_s) if ev_purchase else 0.0
            session_device = device_type
            session_source = traffic_source
            continue

        # new user
        if user_id != current_user:
            output_session(
                current_user, session_index, session_start, session_end,
                event_count, has_view, has_cart, has_purchase,
                revenue, session_device, session_source
            )

            current_user = user_id
            session_index = 1
            session_start = ts
            session_end = ts
            last_ts = ts
            event_count = 1
            has_view = ev_view
            has_cart = ev_cart
            has_purchase = ev_purchase
            revenue = safe_price(price_s) if ev_purchase else 0.0
            session_device = device_type
            session_source = traffic_source
            continue

        # same user: decide session split
        gap_minutes = (ts - last_ts).total_seconds() / 60.0
        midnight_split = (ts.date() != last_ts.date())

        if gap_minutes > SESSION_TIMEOUT_MINUTES or midnight_split:
            output_session(
                current_user, session_index, session_start, session_end,
                event_count, has_view, has_cart, has_purchase,
                revenue, session_device, session_source
            )

            session_index += 1
            session_start = ts
            session_end = ts
            last_ts = ts
            event_count = 1
            has_view = ev_view
            has_cart = ev_cart
            has_purchase = ev_purchase
            revenue = safe_price(price_s) if ev_purchase else 0.0
            session_device = device_type
            session_source = traffic_source
        else:
            session_end = ts
            last_ts = ts
            event_count += 1
            has_view = has_view or ev_view
            has_cart = has_cart or ev_cart
            has_purchase = has_purchase or ev_purchase
            if ev_purchase:
                revenue += safe_price(price_s)

    # Flush last session
    output_session(
        current_user, session_index, session_start, session_end,
        event_count, has_view, has_cart, has_purchase,
        revenue, session_device, session_source
    )

    # Print summary metrics
    print("=== SESSION SUMMARY METRICS ===")
    print(f"Total sessions reconstructed: {total_sessions}")
    if total_sessions > 0:
        avg_dur = total_duration / total_sessions
        avg_events = total_events / total_sessions
        conv_rate = converted_sessions / total_sessions * 100.0
        print(f"Average session duration: {avg_dur:.1f} minutes")
        print(f"Conversion rate: {conv_rate:.1f}%")
        print(f"Average events per session: {avg_events:.1f}")
    if converted_sessions > 0:
        avg_rev = converted_revenue / converted_sessions
        print(f"Average revenue per converted session: ${avg_rev:.2f}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
