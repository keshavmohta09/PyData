"""
This file contains all the urls used for products module
"""

from django.urls import path

from products.apis import product

urlpatterns = [
    path("", product.BulkCreateProductAPI.as_view(), name="product-create"),
    path(
        "summary/", product.RetrieveSummaryReportAPI.as_view(), name="product-summary"
    ),
]
