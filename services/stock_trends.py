from collections import defaultdict
from collections.abc import Iterable
from datetime import date, datetime, timedelta, timezone
from typing import Literal, TypedDict

from models import StockMovement


# ==========================================
# STOCK TREND DATA TYPES
# ==========================================

# Allowed stock movement directions.
MovementType = Literal["IN", "OUT"]


class DailyStockTotals(TypedDict):
    """
    Store stock movement totals for one day.

    Data types:
        IN: int
        OUT: int
    """

    IN: int
    OUT: int


class StockTrends(TypedDict):
    """
    Define the structure of the stock trends report.

    Data types:
        labels: list[str]
        stock_in: list[int]
        stock_out: list[int]
        total_stock_in: int
        total_stock_out: int
        net_change: int
    """

    labels: list[str]
    stock_in: list[int]
    stock_out: list[int]
    total_stock_in: int
    total_stock_out: int
    net_change: int


# ==========================================
# BUILD STOCK TRENDS
# ==========================================


def build_stock_trends(
    movements: Iterable[StockMovement],
    start_date: date,
    end_date: date,
) -> StockTrends:
    """
    Calculate daily Stock In and Stock Out totals.

    Dates are inclusive, and movement timestamps
    are interpreted in UTC.

    Parameters:
        movements (Iterable[StockMovement]):
            Stock movement records.

        start_date (date):
            First date included in the report.

        end_date (date):
            Last date included in the report.

    Returns:
        StockTrends:
            Dictionary containing daily stock totals,
            overall totals, and net stock change.

    Raises:
        ValueError:
            If start_date is after end_date.
    """

    # ======================================
    # VALIDATE DATE RANGE
    # ======================================

    if start_date > end_date:
        raise ValueError("start_date cannot be after end_date")

    # ======================================
    # INITIALIZE DAILY TOTALS
    # ======================================

    # Data type:
    # defaultdict[date, DailyStockTotals]
    daily_totals: defaultdict[
        date,
        DailyStockTotals,
    ] = defaultdict(lambda: {"IN": 0, "OUT": 0})

    # ======================================
    # PROCESS STOCK MOVEMENTS
    # ======================================

    for movement in movements:
        # Data type: datetime
        timestamp: datetime = movement.created_at

        if timestamp.tzinfo is None:
            # Existing SQLite timestamps are
            # interpreted as UTC.
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        else:
            timestamp = timestamp.astimezone(timezone.utc)

        # Data type: date
        movement_date: date = timestamp.date()

        # Ignore movements outside the date range.
        if not start_date <= movement_date <= end_date:
            continue

        # Ignore unsupported movement types.
        if movement.movement_type not in ("IN", "OUT"):
            continue

        # Data type: MovementType
        movement_type: MovementType = "IN" if movement.movement_type == "IN" else "OUT"

        daily_totals[movement_date][movement_type] += movement.quantity

    # ======================================
    # PREPARE CHART DATA
    # ======================================

    # Data type: list[str]
    labels: list[str] = []

    # Data type: list[int]
    stock_in: list[int] = []

    # Data type: list[int]
    stock_out: list[int] = []

    # Data type: date
    current_date: date = start_date

    while current_date <= end_date:
        # Data type: DailyStockTotals
        totals: DailyStockTotals = daily_totals[current_date]

        labels.append(current_date.isoformat())

        stock_in.append(totals["IN"])

        stock_out.append(totals["OUT"])

        current_date += timedelta(days=1)

    # ======================================
    # CALCULATE SUMMARY TOTALS
    # ======================================

    # Data type: int
    total_stock_in: int = sum(stock_in)

    # Data type: int
    total_stock_out: int = sum(stock_out)

    # Data type: int
    net_change: int = total_stock_in - total_stock_out

    # ======================================
    # BUILD FINAL REPORT
    # ======================================

    # Data type: StockTrends
    trends: StockTrends = {
        "labels": labels,
        "stock_in": stock_in,
        "stock_out": stock_out,
        "total_stock_in": total_stock_in,
        "total_stock_out": total_stock_out,
        "net_change": net_change,
    }

    return trends
