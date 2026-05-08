from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import RegistrationForm


@login_required
def dashboard(request):
    user = request.user
    if user.is_superuser:
        account_type = "Superuser account"
    elif user.is_staff:
        account_type = "Staff account"
    else:
        account_type = "Regular customer account"

    return render(
        request,
        "accounts/dashboard.html",
        {
            "account_type": account_type,
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
