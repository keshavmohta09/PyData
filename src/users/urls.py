"""
This file contains all the urls used for users module
"""

from django.urls import path

from users.apis import auth, user

urlpatterns = [
    path("login/", auth.UserLoginAPI.as_view(), name="user-login"),
    path("signup/", user.UserSignupAPI.as_view(), name="user-signup"),
    path("login/refresh/", auth.UserRefreshAPI.as_view(), name="user-login-refresh"),
    path("logout/", auth.UserLogoutAPI.as_view(), name="user-logout"),
]
