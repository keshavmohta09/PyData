"""
This file contains all the APIs related to user model
"""

from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from users.constants import PASSWORDS_DO_NOT_MATCH
from users.models import User
from utils.constants import OBJECT_CREATED_SUCCESSFULLY
from utils.response import CustomResponse


class UserSignupAPI(APIView):
    """
    This API is used to sign up a new user.
    Response codes: 201, 400
    """

    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        first_name = serializers.CharField(max_length=256)
        last_name = serializers.CharField(
            max_length=256, required=False, allow_blank=True
        )
        password = serializers.CharField(min_length=8, write_only=True)
        confirm_password = serializers.CharField(min_length=8, write_only=True)

        def validate(self, data):
            if data["password"] != data["confirm_password"]:
                raise serializers.ValidationError(PASSWORDS_DO_NOT_MATCH)
            return data

    def post(self, request, *args, **kwargs):
        serializer = self.InputSerializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse(errors=serializer.errors, status=HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data

        # Extract and prepare user data
        email = validated_data["email"]
        first_name = validated_data["first_name"]
        last_name = validated_data.get("last_name", "")
        password = validated_data["password"]

        try:
            # Create user with provided details
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=make_password(password),  # Hash the password
            )
            user.full_clean()
            user.save()
        except (IntegrityError, ValidationError) as error:
            return CustomResponse(errors=error, status=HTTP_400_BAD_REQUEST)

        return CustomResponse(
            data=OBJECT_CREATED_SUCCESSFULLY.format(object="User"),
            status=HTTP_201_CREATED,
        )
