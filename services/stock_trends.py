
from collections import defaultdict
from datetime import datetime, timedelta, timezone


def build_stock_trends(movements, start_date, end_date):
    """
    Calculate daily Stock In and Stock Out totals.

    Dates are inclusive, and movement timestamps are
    interpreted in UTC.
    """
    if start_date > end_date:
        raise ValueError(
            "start_date cannot be after end_date"
        )

    daily_totals = defaultdict(
        lambda: {"IN": 0, "OUT": 0}
    )

    for movement in movements:
        timestamp = movement.created_at

        if timestamp.tzinfo is None:
            # Existing SQLite timestamps are stored as UTC.
            timestamp = timestamp.replace(
                tzinfo=timezone.utc
            )
        else:
            timestamp = timestamp.astimezone(
                timezone.utc
            )

        movement_date = timestamp.date()

        if not start_date <= movement_date <= end_date:
            continue

        if movement.movement_type not in ("IN", "OUT"):
            continue

        daily_totals[movement_date][
            movement.movement_type
        ] += movement.quantity

    labels = []
    stock_in = []
    stock_out = []

    current_date = start_date

    while current_date <= end_date:
        totals = daily_totals[current_date]

        labels.append(
            current_date.isoformat()
        )
        stock_in.append(
            totals["IN"]
        )
        stock_out.append(
            totals["OUT"]
        )

        current_date += timedelta(days=1)

    total_stock_in = sum(stock_in)
    total_stock_out = sum(stock_out)

    return {
        "labels": labels,
        "stock_in": stock_in,
        "stock_out": stock_out,
        "total_stock_in": total_stock_in,
        "total_stock_out": total_stock_out,
        "net_change": (
            total_stock_in - total_stock_out
        ),
    }