from django.urls import path
from . import views

app_name = "accounts"  # app_name will help us do a reverse look-up latter.

urlpatterns = [
    path("details/", views.UserAccountView, name="user_account"),
]
