from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView,
)

from core.mixins import RoleRequiredMixin
from .forms import LoginForm, ProfileForm, UserRegistrationForm, UserUpdateForm
from .models import Role, User


class AluflowLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


class AluflowLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:login")


@login_required
def profile_view(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=request.user)
    return render(request, "accounts/profile.html", {"form": form})


class UserListView(RoleRequiredMixin, ListView):
    model = User
    template_name = "accounts/user_list.html"
    context_object_name = "users"
    paginate_by = 20
    allowed_roles = (Role.ADMIN, Role.MANAGER)


class UserCreateView(RoleRequiredMixin, CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("accounts:user_list")
    allowed_roles = (Role.ADMIN, Role.MANAGER)

    def form_valid(self, form):
        messages.success(self.request, "User created.")
        return super().form_valid(form)


class UserUpdateView(RoleRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("accounts:user_list")
    allowed_roles = (Role.ADMIN, Role.MANAGER)


class UserDeleteView(RoleRequiredMixin, DeleteView):
    model = User
    template_name = "accounts/user_confirm_delete.html"
    success_url = reverse_lazy("accounts:user_list")
    allowed_roles = (Role.ADMIN,)
