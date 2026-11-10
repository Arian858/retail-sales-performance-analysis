
"""
Retail Sales Analysis Module
----------------------------
Reusable functions for validating retail transaction data,
calculating business KPIs, and evaluating sales performance.
"""

import numpy as np
import pandas as pd


# --------------------------------------------------
# 1. REQUIRED DATA COLUMNS
# --------------------------------------------------

REQUIRED_COLUMNS = {
    "order_id",
    "order_date",
    "customer_id",
    "region",
    "sales_channel",
    "category",
    "unit_price",
    "quantity",
    "discount_pct",
    "gross_revenue",
    "discount_amount",
    "net_revenue",
}


# --------------------------------------------------
# 2. DATA VALIDATION
# --------------------------------------------------

def validate_sales_data(df: pd.DataFrame) -> None:
    """Validate the structure and financial consistency of sales data."""

    missing_columns = REQUIRED_COLUMNS - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    if df.empty:
        raise ValueError("The sales dataset is empty.")

    if df[list(REQUIRED_COLUMNS)].isnull().any().any():
        raise ValueError("The dataset contains missing required values.")

    if df["order_id"].duplicated().any():
        raise ValueError("Duplicate order identifiers detected.")

    if (df["unit_price"] <= 0).any():
        raise ValueError("Unit prices must be positive.")

    if (df["quantity"] <= 0).any():
        raise ValueError("Quantities must be positive.")

    if not df["discount_pct"].between(0, 1).all():
        raise ValueError("Discount percentages must be between 0 and 1.")

    monetary_columns = [
        "gross_revenue",
        "discount_amount",
        "net_revenue",
    ]

    if (df[monetary_columns] < 0).any().any():
        raise ValueError("Revenue values cannot be negative.")

    expected_gross = (
        df["unit_price"] * df["quantity"]
    )

    if not np.isclose(
        expected_gross,
        df["gross_revenue"],
        atol=0.01,
        rtol=0
    ).all():
        raise ValueError("Gross revenue calculations are inconsistent.")

    expected_discount = (
        df["gross_revenue"] * df["discount_pct"]
    )

    if not np.isclose(
        expected_discount,
        df["discount_amount"],
        atol=0.01,
        rtol=0
    ).all():
        raise ValueError("Discount calculations are inconsistent.")

    expected_net = (
        df["gross_revenue"] - df["discount_amount"]
    )

    if not np.isclose(
        expected_net,
        df["net_revenue"],
        atol=0.01,
        rtol=0
    ).all():
        raise ValueError("Net revenue calculations are inconsistent.")


# --------------------------------------------------
# 3. BUSINESS KPI CALCULATIONS
# --------------------------------------------------

def calculate_kpis(df: pd.DataFrame) -> dict:
    """Calculate the principal retail business KPIs."""

    validate_sales_data(df)

    total_revenue = df["net_revenue"].sum()
    total_orders = df["order_id"].nunique()

    return {
        "total_revenue": float(total_revenue),

        "total_orders": int(total_orders),

        "average_order_value": float(
            total_revenue / total_orders
        ),

        "total_units_sold": int(
            df["quantity"].sum()
        ),

        "total_customers": int(
            df["customer_id"].nunique()
        ),

        "total_discounts": float(
            df["discount_amount"].sum()
        ),
    }


# --------------------------------------------------
# 4. GENERIC PERFORMANCE ANALYSIS
# --------------------------------------------------

def _summarize_dimension(
    df: pd.DataFrame,
    dimension: str
) -> pd.DataFrame:
    """Summarize sales performance for a specified dimension."""

    validate_sales_data(df)

    allowed_dimensions = {
        "category",
        "region",
        "sales_channel",
    }

    if dimension not in allowed_dimensions:
        raise ValueError(
            f"Unsupported analytical dimension: {dimension}"
        )

    summary = (
        df.groupby(dimension)
        .agg(
            total_revenue=("net_revenue", "sum"),
            total_orders=("order_id", "nunique"),
            units_sold=("quantity", "sum"),
            unique_customers=("customer_id", "nunique"),
            average_order_value=("net_revenue", "mean"),
            total_discounts=("discount_amount", "sum"),
        )
        .reset_index()
    )

    overall_revenue = df["net_revenue"].sum()

    if overall_revenue != 0:
        summary["revenue_contribution_pct"] = (
            summary["total_revenue"]
            / overall_revenue * 100
        )
    else:
        summary["revenue_contribution_pct"] = 0.0

    return (
        summary
        .sort_values("total_revenue", ascending=False)
        .reset_index(drop=True)
    )


# --------------------------------------------------
# 5. PUBLIC PERFORMANCE FUNCTIONS
# --------------------------------------------------

def summarize_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize performance by product category."""

    return _summarize_dimension(df, "category")


def summarize_by_region(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize performance by geographical region."""

    return _summarize_dimension(df, "region")


def summarize_by_sales_channel(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize performance by sales channel."""

    return _summarize_dimension(df, "sales_channel")
