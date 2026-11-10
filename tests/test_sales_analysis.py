
"""
Automated tests for the retail sales analysis module.
"""

import pandas as pd
import pytest

from src.sales_analysis import (
    validate_sales_data,
    calculate_kpis,
    summarize_by_category,
)


@pytest.fixture
def sample_sales_data():
    """Create a small, predictable test dataset."""

    return pd.DataFrame({
        "order_id": ["O001", "O002", "O003"],
        "order_date": pd.to_datetime([
            "2025-01-01",
            "2025-01-02",
            "2025-01-03",
        ]),
        "customer_id": ["C001", "C001", "C002"],
        "region": ["North", "South", "North"],
        "sales_channel": ["Online", "Physical Store", "Online"],
        "category": ["Books", "Electronics", "Books"],
        "unit_price": [10.0, 20.0, 5.0],
        "quantity": [2, 1, 4],
        "discount_pct": [0.10, 0.00, 0.20],
        "gross_revenue": [20.0, 20.0, 20.0],
        "discount_amount": [2.0, 0.0, 4.0],
        "net_revenue": [18.0, 20.0, 16.0],
    })


# --------------------------------------------------
# TEST 1: DATA VALIDATION
# --------------------------------------------------

def test_valid_sales_data(sample_sales_data):

    result = validate_sales_data(sample_sales_data)

    assert result is None


# --------------------------------------------------
# TEST 2: KPI CALCULATIONS
# --------------------------------------------------

def test_calculate_kpis(sample_sales_data):

    kpis = calculate_kpis(sample_sales_data)

    assert kpis["total_revenue"] == pytest.approx(54.0)

    assert kpis["total_orders"] == 3

    assert kpis["average_order_value"] == pytest.approx(18.0)

    assert kpis["total_units_sold"] == 7

    assert kpis["total_customers"] == 2

    assert kpis["total_discounts"] == pytest.approx(6.0)


# --------------------------------------------------
# TEST 3: CATEGORY PERFORMANCE
# --------------------------------------------------

def test_category_performance(sample_sales_data):

    result = summarize_by_category(sample_sales_data)

    books = result.loc[
        result["category"] == "Books"
    ].iloc[0]

    assert books["total_revenue"] == pytest.approx(34.0)

    assert books["total_orders"] == 2

    assert books["units_sold"] == 6

    assert books["revenue_contribution_pct"] == pytest.approx(
        34 / 54 * 100
    )


# --------------------------------------------------
# TEST 4: DUPLICATE ORDER DETECTION
# --------------------------------------------------

def test_duplicate_orders_are_rejected(sample_sales_data):

    sample_sales_data.loc[1, "order_id"] = "O001"

    with pytest.raises(ValueError, match="Duplicate order"):
        validate_sales_data(sample_sales_data)


# --------------------------------------------------
# TEST 5: INVALID REVENUE DETECTION
# --------------------------------------------------

def test_inconsistent_revenue_is_rejected(sample_sales_data):

    sample_sales_data.loc[0, "net_revenue"] = 999.0

    with pytest.raises(ValueError, match="Net revenue"):
        validate_sales_data(sample_sales_data)


# --------------------------------------------------
# TEST 6: MISSING COLUMN DETECTION
# --------------------------------------------------

def test_missing_required_column_is_rejected(sample_sales_data):

    sample_sales_data = sample_sales_data.drop(
        columns=["customer_id"]
    )

    with pytest.raises(ValueError, match="Missing required columns"):
        validate_sales_data(sample_sales_data)
