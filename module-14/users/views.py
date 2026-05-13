from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from .forms import EmailAuthenticationForm, UserRegistrationForm


class CustomLoginView(LoginView):
    """Custom login view using Django's built-in LoginView."""

    template_name = 'accounts/login.html'
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    """Custom logout view redirecting to the home page."""

    next_page = 'shop:home'


class RegisterView(FormView):
    """User registration view."""

    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('shop:home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Handle successful form submission."""
        form.save()
        messages.success(self.request, 'Registration successful! You can now log in.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Register'
        return context
