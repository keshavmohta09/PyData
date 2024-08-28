"""
This file contains all the apis used for products module
"""

import pandas as pd
from django.core.validators import FileExtensionValidator
from django.db import transaction
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from products.helpers import clean_product_data, generate_summary_report
from products.models import Product
from utils.response import CustomResponse


class BulkCreateProductAPI(APIView):
    """
    This API is used to bulk creating products by uploading a csv file
    """

    permission_classes = (IsAuthenticated,)

    class InputSerializer(serializers.Serializer):
        file = serializers.FileField(
            validators=[FileExtensionValidator(allowed_extensions=("csv",))]
        )

        def validate(self, attrs):
            file = attrs.get("file")
            try:
                # Read the CSV file into a pandas DataFrame
                df = pd.read_csv(file)
                # Clean the file data
                validated_df = clean_product_data(df=df)
                attrs["data"] = validated_df
            except Exception as error:
                raise serializers.ValidationError(
                    f"Error processing CSV file: {str(error)}"
                )

            return attrs

    def post(self, request, *args, **kwargs):
        serializer = self.InputSerializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse(errors=serializer.errors, status=HTTP_400_BAD_REQUEST)

        df = serializer.validated_data["data"]
        # Separate data into rows for update and creation
        existing_products = {
            product.product_id: product for product in Product.objects.all()
        }

        try:
            products_to_create = df[~df["product_id"].isin(list(existing_products))]
            products_to_update = df[df["product_id"].isin(list(existing_products))]

            product_create_list = []
            product_update_list = []

            for _, row in products_to_create.iterrows():
                product = Product(
                    product_id=row["product_id"],
                    product_name=row["product_name"],
                    category=row["category"],
                    price=row["price"],
                    quantity_sold=row["quantity_sold"],
                    rating=row["rating"],
                    review_count=row["review_count"],
                )
                product.clean_fields()
                product.clean()
                product_create_list.append(product)

            for _, row in products_to_update.iterrows():
                product = existing_products[row["product_id"]]

                product.product_name = row["product_name"]
                product.category = row["category"]
                product.price = row["price"]
                product.quantity_sold = row["quantity_sold"]
                product.rating = row["rating"]
                product.review_count = row["review_count"]

                product.clean_fields()
                product.clean()
                product_update_list.append(product)

            with transaction.atomic():
                Product.objects.bulk_create(product_create_list)
                Product.objects.bulk_update(
                    product_update_list,
                    fields=[
                        "product_name",
                        "category",
                        "price",
                        "quantity_sold",
                        "rating",
                        "review_count",
                    ],
                )

        except Exception as error:
            return CustomResponse(errors=error, status=HTTP_400_BAD_REQUEST)

        return CustomResponse(status=HTTP_204_NO_CONTENT)


class RetrieveSummaryReportAPI(APIView):
    """
    This API is used to generate and download a summary report as a CSV file.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        # Generate the summary report
        response = generate_summary_report()

        return response
