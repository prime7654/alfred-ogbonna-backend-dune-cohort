from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views
from .forms import EmailOrUsernameAuthenticationForm


app_name = "accounts"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("my-account/", views.my_account, name="my_account"),
    path(
        "login/",
        LoginView.as_view(
            authentication_form=EmailOrUsernameAuthenticationForm,
            redirect_authenticated_user=True,
            template_name="accounts/login.html",
        ),
        name="login",
    ),
    path("logout/", LogoutView.as_view(next_page="shop:home"), name="logout"),
    path("register/", views.register, name="register"),
]
