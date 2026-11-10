
"""
Retail Sales Dataset Generator
--------------------------------
Generates a reproducible synthetic retail transaction
dataset for the Retail Sales Performance Analysis project.

Dataset period: 2024-2025
Number of transactions: 1,500
"""

from pathlib import Path

import numpy as np
import pandas as pd


# --------------------------------------------------
# 1. PROJECT CONFIGURATION
# --------------------------------------------------

RANDOM_SEED = 42
N_TRANSACTIONS = 1500

rng = np.random.default_rng(RANDOM_SEED)


# --------------------------------------------------
# 2. PRODUCT CATALOG
# --------------------------------------------------

PRODUCTS = [
    {"product_id": "P001", "product_name": "Smartphone", "category": "Electronics", "unit_price": 699.00},
    {"product_id": "P002", "product_name": "Laptop", "category": "Electronics", "unit_price": 1199.00},
    {"product_id": "P003", "product_name": "Headphones", "category": "Electronics", "unit_price": 149.00},
    {"product_id": "P004", "product_name": "Monitor", "category": "Electronics", "unit_price": 279.00},
    {"product_id": "P005", "product_name": "Coffee Maker", "category": "Home & Kitchen", "unit_price": 89.00},
    {"product_id": "P006", "product_name": "Blender", "category": "Home & Kitchen", "unit_price": 59.00},
    {"product_id": "P007", "product_name": "Air Fryer", "category": "Home & Kitchen", "unit_price": 129.00},
    {"product_id": "P008", "product_name": "Vacuum Cleaner", "category": "Home & Kitchen", "unit_price": 229.00},
    {"product_id": "P009", "product_name": "T-Shirt", "category": "Clothing", "unit_price": 25.00},
    {"product_id": "P010", "product_name": "Jeans", "category": "Clothing", "unit_price": 65.00},
    {"product_id": "P011", "product_name": "Jacket", "category": "Clothing", "unit_price": 110.00},
    {"product_id": "P012", "product_name": "Yoga Mat", "category": "Sports & Outdoors", "unit_price": 35.00},
    {"product_id": "P013", "product_name": "Dumbbell Set", "category": "Sports & Outdoors", "unit_price": 75.00},
    {"product_id": "P014", "product_name": "Running Shoes", "category": "Sports & Outdoors", "unit_price": 95.00},
    {"product_id": "P015", "product_name": "Fiction Bestseller", "category": "Books", "unit_price": 18.00},
    {"product_id": "P016", "product_name": "Technical Book", "category": "Books", "unit_price": 45.00},
]

products_df = pd.DataFrame(PRODUCTS)


# --------------------------------------------------
# 3. REGIONAL INFORMATION
# --------------------------------------------------

REGION_CITIES = {
    "North": ["Toronto", "Ottawa", "Montreal"],
    "South": ["New York", "Boston", "Philadelphia"],
    "East": ["Berlin", "Hamburg", "Munich"],
    "West": ["Vancouver", "Calgary", "Seattle"],
}

regions = list(REGION_CITIES.keys())


# --------------------------------------------------
# 4. GENERATE TRANSACTION DETAILS
# --------------------------------------------------

product_indices = rng.integers(
    0, len(products_df), size=N_TRANSACTIONS
)

selected_products = (
    products_df.iloc[product_indices]
    .reset_index(drop=True)
)

selected_regions = rng.choice(
    regions, size=N_TRANSACTIONS
)

cities = [
    rng.choice(REGION_CITIES[region])
    for region in selected_regions
]

# Generate dates between January 1, 2024
# and December 31, 2025.

start_date = pd.Timestamp("2024-01-01")

order_dates = start_date + pd.to_timedelta(
    rng.integers(0, 731, size=N_TRANSACTIONS),
    unit="D"
)

quantities = rng.choice(
    [1, 2, 3, 4, 5],
    size=N_TRANSACTIONS,
    p=[0.42, 0.30, 0.16, 0.08, 0.04]
)

discount_rates = rng.choice(
    [0.00, 0.05, 0.10, 0.15, 0.20],
    size=N_TRANSACTIONS,
    p=[0.45, 0.20, 0.18, 0.12, 0.05]
)

sales_channels = rng.choice(
    ["Online", "Physical Store", "Partner"],
    size=N_TRANSACTIONS,
    p=[0.50, 0.35, 0.15]
)

payment_methods = rng.choice(
    ["Credit Card", "Debit Card", "PayPal", "Cash"],
    size=N_TRANSACTIONS,
    p=[0.40, 0.30, 0.15, 0.15]
)

customer_ids = [
    f"C{number:04d}"
    for number in rng.integers(1, 301, size=N_TRANSACTIONS)
]


# --------------------------------------------------
# 5. CALCULATE REVENUE
# --------------------------------------------------

unit_prices = selected_products["unit_price"].to_numpy()

gross_revenue = unit_prices * quantities

discount_amount = gross_revenue * discount_rates

net_revenue = gross_revenue - discount_amount


# --------------------------------------------------
# 6. BUILD THE FINAL DATASET
# --------------------------------------------------

sales_df = pd.DataFrame({
    "order_id": [
        f"ORD-{number:06d}"
        for number in range(1, N_TRANSACTIONS + 1)
    ],
    "order_date": order_dates,
    "customer_id": customer_ids,
    "region": selected_regions,
    "city": cities,
    "sales_channel": sales_channels,
    "product_id": selected_products["product_id"],
    "product_name": selected_products["product_name"],
    "category": selected_products["category"],
    "unit_price": unit_prices,
    "quantity": quantities,
    "discount_pct": discount_rates,
    "gross_revenue": gross_revenue,
    "discount_amount": discount_amount,
    "net_revenue": net_revenue,
    "payment_method": payment_methods,
})

sales_df = (
    sales_df.sort_values("order_date")
    .reset_index(drop=True)
)

# Round monetary values to two decimal places.
monetary_columns = [
    "unit_price",
    "gross_revenue",
    "discount_amount",
    "net_revenue",
]

sales_df[monetary_columns] = (
    sales_df[monetary_columns].round(2)
)


# --------------------------------------------------
# 7. EXPORT THE DATASET
# --------------------------------------------------

project_root = Path(__file__).resolve().parents[1]

output_directory = project_root / "data" / "raw"

output_directory.mkdir(
    parents=True,
    exist_ok=True
)

output_path = output_directory / "retail_sales.csv"

sales_df.to_csv(output_path, index=False)


# --------------------------------------------------
# 8. GENERATION SUMMARY
# --------------------------------------------------

print("=" * 55)
print("       RETAIL SALES DATASET GENERATION")
print("=" * 55)

print(f"\nTransactions generated: {len(sales_df):,}")

print(
    f"Date range: "
    f"{sales_df['order_date'].min():%Y-%m-%d} "
    f"to "
    f"{sales_df['order_date'].max():%Y-%m-%d}"
)

print(f"Products available: {sales_df['product_id'].nunique()}")
print(f"Regions covered: {sales_df['region'].nunique()}")

print(
    f"Total net revenue: "
    f"${sales_df['net_revenue'].sum():,.2f}"
)

print(f"\nDataset saved successfully:\n{output_path}")

print("\nFirst five transactions:")
print(sales_df.head().to_string(index=False))

print("\nDataset generation completed successfully.")
