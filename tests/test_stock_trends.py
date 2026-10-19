
from datetime import datetime, date, timezone
from datetime import timedelta
from types import SimpleNamespace

import pytest

from services.stock_trends import build_stock_trends


def make_movement(day, movement_type, quantity):
    """Create a sample stock movement for testing."""
    return SimpleNamespace(
        created_at=datetime(
            2026, 10, day, 12, 0,
            tzinfo=timezone.utc,
        ),
        movement_type=movement_type,
        quantity=quantity,
    )


def test_stock_in_and_out_totals():
    movements = [
        make_movement(10, "IN", 20),
        make_movement(10, "IN", 5),
        make_movement(10, "OUT", 8),
        make_movement(11, "OUT", 3),
    ]

    result = build_stock_trends(
        movements,
        date(2026, 10, 10),
        date(2026, 10, 11),
    )

    assert result["labels"] == [
        "2026-10-10",
        "2026-10-11",
    ]
    assert result["stock_in"] == [25, 0]
    assert result["stock_out"] == [8, 3]
    assert result["total_stock_in"] == 25
    assert result["total_stock_out"] == 11
    assert result["net_change"] == 14


def test_days_without_movements():
    movements = [
        make_movement(10, "IN", 5),
        make_movement(12, "OUT", 2),
    ]

    result = build_stock_trends(
        movements,
        date(2026, 10, 10),
        date(2026, 10, 12),
    )

    assert result["stock_in"] == [5, 0, 0]
    assert result["stock_out"] == [0, 0, 2]


def test_movements_outside_date_range_are_excluded():
    movements = [
        make_movement(9, "IN", 100),
        make_movement(10, "IN", 10),
        make_movement(12, "OUT", 50),
    ]

    result = build_stock_trends(
        movements,
        date(2026, 10, 10),
        date(2026, 10, 11),
    )

    assert result["total_stock_in"] == 10
    assert result["total_stock_out"] == 0


def test_empty_movements():
    result = build_stock_trends(
        [],
        date(2026, 10, 10),
        date(2026, 10, 11),
    )

    assert result["stock_in"] == [0, 0]
    assert result["stock_out"] == [0, 0]
    assert result["net_change"] == 0


def test_invalid_date_range():
    with pytest.raises(
        ValueError,
        match="start_date cannot be after end_date",
    ):
        build_stock_trends(
            [],
            date(2026, 10, 12),
            date(2026, 10, 10),
        )


def test_unknown_movement_type_is_ignored():
    movements = [
        make_movement(10, "ADJUSTMENT", 100),
        make_movement(10, "IN", 7),
    ]

    result = build_stock_trends(
        movements,
        date(2026, 10, 10),
        date(2026, 10, 10),
    )

    assert result["total_stock_in"] == 7
    assert result["total_stock_out"] == 0


def test_timezone_aware_movement_uses_utc_date():
    """A movement's UTC date determines its reporting day."""

    movement = SimpleNamespace(
        created_at=datetime(
            2026, 10, 20, 1, 30,
            tzinfo=timezone(timedelta(hours=3)),
        ),
        movement_type="IN",
        quantity=12,
    )

    result = build_stock_trends(
        [movement],
        date(2026, 10, 19),
        date(2026, 10, 20),
    )

    assert result["labels"] == [
        "2026-10-19",
        "2026-10-20",
    ]

    assert result["stock_in"] == [12, 0]
    assert result["total_stock_in"] == 12