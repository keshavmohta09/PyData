"""
This file contains all the models for products module
"""

from django.db import models


class Product(models.Model):
    product_id = models.CharField(max_length=255, unique=True)
    product_name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_sold = models.PositiveIntegerField()
    rating = models.FloatField()
    review_count = models.PositiveIntegerField()

    def __str__(self):
        return self.product_name
