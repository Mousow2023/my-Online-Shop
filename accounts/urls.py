from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("register/", views.register, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),

    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
    path("forgot_password/", views.forgot_password, name="forgot_password"),
    path("reset_password_validate/<uidb64>/<token>/", views.reset_password_validate, name="reset_password_validate"),
    path("reset_password/", views.reset_password, name="reset_password"),

    path("my_orders/", views.my_orders, name="my_orders"),
    path("edit_profile/", views.edit_profile, name="edit_profile"),
]
