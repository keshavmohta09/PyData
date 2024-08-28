"""
This file contains all the model admins for products module
"""

from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product_id",
        "product_name",
        "category",
        "price",
        "quantity_sold",
        "rating",
        "review_count",
    )
    list_filter = ("category", "rating")
    search_fields = ("product_id", "product_name", "category")
