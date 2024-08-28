"""
This file contains all the helpers used for products module
"""

import csv

import pandas as pd
from django.db.models import F, OuterRef, Subquery, Sum
from django.http import HttpResponse

from products.models import Product


def clean_product_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the DataFrame by handling missing values and ensuring data types.

    Params:
        df (pd.DataFrame): The DataFrame to be cleaned.

    Output:
        pd.DataFrame: The cleaned DataFrame.
    """

    # Ensure required columns are present
    required_columns = {
        "product_id",
        "product_name",
        "category",
        "price",
        "quantity_sold",
        "rating",
        "review_count",
    }
    if not required_columns.issubset(df.columns):
        missing_columns = required_columns - set(df.columns)
        raise ValueError(
            f"DataFrame missing required columns: {', '.join(missing_columns)}"
        )

    # Convert columns to numeric, coercing errors to NaN
    breakpoint()
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["quantity_sold"] = pd.to_numeric(df["quantity_sold"], errors="coerce")
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

    # Replace missing values
    # Replace missing values with median for `price` and `quantity_sold`
    df["price"].fillna(df["price"].median(), inplace=True)
    df["quantity_sold"].fillna(df["quantity_sold"].median(), inplace=True)

    # Drop rows with missing `product_id` as it is necessary for uniqueness
    df.dropna(subset=["product_id"], inplace=True)

    # Ensure data types are correct
    df["product_id"] = df["product_id"].astype(str)  # Ensure product_id is string
    df["product_name"] = df["product_name"].astype(str)  # Ensure product_name is string
    df["category"] = df["category"].astype(str)  # Ensure category is string
    df["review_count"] = (
        df["review_count"].fillna(0).astype(int)
    )  # Ensure review_count is integer

    return df


def generate_summary_report() -> HttpResponse:
    """
    Generate a summary report from the Product data and return it as a CSV file.
    Output:
        HttpResponse: The CSV file containing the summary report.
    """

    # Subquery to get the top product in each category by quantity_sold
    top_product_subquery = (
        Product.objects.filter(category=OuterRef("category"))
        .order_by("-quantity_sold")
        .values("product_name")[:1]
    )

    top_product_quantity_subquery = Product.objects.filter(
        category=OuterRef("category"), product_name=Subquery(top_product_subquery)
    ).values("quantity_sold")[:1]

    # Aggregate data to get total revenue and top product
    summary_data = (
        Product.objects.values("category")
        .annotate(
            total_revenue=Sum(F("price") * F("quantity_sold")),
            top_product=Subquery(top_product_subquery),
            top_product_quantity_sold=Subquery(top_product_quantity_subquery),
        )
        .order_by("category")
    )

    # Create CSV response
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="summary_report.csv"'

    writer = csv.writer(response)
    writer.writerow(
        ["category", "total_revenue", "top_product", "top_product_quantity_sold"]
    )

    for entry in summary_data:
        writer.writerow(
            [
                entry["category"],
                entry["total_revenue"],
                entry["top_product"],
                entry["top_product_quantity_sold"],
            ]
        )

    return response
