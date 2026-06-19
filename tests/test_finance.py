"""Lightweight tests for the Finance module (no DB required).

Run with: pytest tests/test_finance.py
"""
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.api.v1.finance import _resolve_period
from app.schemas.finance import (
    FinanceSummaryResponse,
    FinanceTransactionCreate,
    CategoryBreakdown,
)


def test_resolve_period_explicit_range_wins():
    df = datetime(2026, 1, 1, tzinfo=timezone.utc)
    dt = datetime(2026, 1, 31, tzinfo=timezone.utc)
    start, end = _resolve_period("this_month", df, dt)
    assert start == df
    assert end == dt


def test_resolve_period_today():
    start, end = _resolve_period("today", None, None)
    assert start.hour == 0 and start.minute == 0
    assert end >= start


def test_resolve_period_default_is_30_days():
    start, end = _resolve_period("this_month", None, None)
    assert (end - start).days in (29, 30)


def test_transaction_create_validates_type():
    with pytest.raises(Exception):
        FinanceTransactionCreate(
            type="invalid",
            category="feed",
            amount=Decimal("1000"),
            recorded_at=datetime.now(timezone.utc),
        )


def test_transaction_create_rejects_non_positive_amount():
    with pytest.raises(Exception):
        FinanceTransactionCreate(
            type="expense",
            category="feed",
            amount=Decimal("0"),
            recorded_at=datetime.now(timezone.utc),
        )


def test_transaction_create_defaults_currency_uzs():
    tx = FinanceTransactionCreate(
        type="income",
        category="milk_sale",
        amount=Decimal("500000"),
        recorded_at=datetime.now(timezone.utc),
    )
    assert tx.currency == "UZS"


def test_summary_response_net_profit_shape():
    summary = FinanceSummaryResponse(
        farm_id="00000000-0000-0000-0000-000000000001",
        period="this_month",
        date_from=datetime.now(timezone.utc),
        date_to=datetime.now(timezone.utc),
        total_income=1000000.0,
        total_expense=600000.0,
        net_profit=400000.0,
        currency="UZS",
        income_by_category=[CategoryBreakdown(category="milk_sale", total=1000000.0, count=3)],
        expense_by_category=[CategoryBreakdown(category="feed", total=600000.0, count=2)],
    )
    assert summary.net_profit == 400000.0
    assert summary.income_by_category[0].category == "milk_sale"
