from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import RegistrationForm
from products.models import Order


@login_required
def dashboard(request):
    user = request.user
    if not (user.is_staff or user.is_superuser):
        messages.error(request, "Only staff users can view the dashboard.")
        return redirect("shop:home")

    if user.is_superuser:
        account_type = "Superuser account"
    else:
        account_type = "Staff account"

    return render(
        request,
        "accounts/dashboard.html",
        {
            "account_type": account_type,
        },
    )


@login_required
def my_account(request):
    orders = (
        Order.objects.filter(user=request.user)
        .prefetch_related("items")
        .order_by("-created_at")
    )
    return render(
        request,
        "accounts/my_account.html",
        {
            "orders": orders,
        },
    )


def register(request):
    if request.user.is_authenticated:
        return redirect("shop:home")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Your account is ready.")
            return redirect("shop:home")
    else:
        form = RegistrationForm()

    return render(request, "accounts/register.html", {"form": form})
