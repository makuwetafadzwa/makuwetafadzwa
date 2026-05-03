from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from core.mixins import AuditMixin
from .forms import CustomerForm, ProjectForm
from .models import Customer, Project


class CustomerListView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = "customers/customer_list.html"
    context_object_name = "customers"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(
                Q(full_name__icontains=q)
                | Q(company_name__icontains=q)
                | Q(phone__icontains=q)
                | Q(email__icontains=q)
                | Q(customer_code__icontains=q)
            )
        return qs


class CustomerDetailView(LoginRequiredMixin, DetailView):
    model = Customer
    template_name = "customers/customer_detail.html"
    context_object_name = "customer"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["projects"] = self.object.projects.all()
        ctx["quotations"] = self.object.quotations.all() if hasattr(self.object, "quotations") else []
        return ctx


class CustomerCreateView(LoginRequiredMixin, AuditMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = "customers/customer_form.html"

    def get_success_url(self):
        return self.object.get_absolute_url()


class CustomerUpdateView(LoginRequiredMixin, AuditMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = "customers/customer_form.html"


class CustomerDeleteView(LoginRequiredMixin, DeleteView):
    model = Customer
    template_name = "customers/customer_confirm_delete.html"
    success_url = reverse_lazy("customers:list")


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = "customers/project_list.html"
    context_object_name = "projects"
    paginate_by = 20


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = "customers/project_detail.html"
    context_object_name = "project"


class ProjectCreateView(LoginRequiredMixin, AuditMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "customers/project_form.html"

    def get_initial(self):
        initial = super().get_initial()
        cid = self.request.GET.get("customer")
        if cid:
            initial["customer"] = cid
        return initial

    def get_success_url(self):
        return self.object.get_absolute_url()


class ProjectUpdateView(LoginRequiredMixin, AuditMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "customers/project_form.html"


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = "customers/project_confirm_delete.html"
    success_url = reverse_lazy("customers:project_list")
