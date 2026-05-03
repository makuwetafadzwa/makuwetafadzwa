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
from customers.models import Customer, Project
from .forms import LeadActivityForm, LeadConvertForm, LeadForm
from .models import Lead, LeadStatus


class LeadListView(LoginRequiredMixin, ListView):
    model = Lead
    template_name = "leads/lead_list.html"
    context_object_name = "leads"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        status = self.request.GET.get("status")
        source = self.request.GET.get("source")
        if q:
            qs = qs.filter(
                Q(full_name__icontains=q)
                | Q(phone__icontains=q)
                | Q(email__icontains=q)
                | Q(company__icontains=q)
            )
        if status:
            qs = qs.filter(status=status)
        if source:
            qs = qs.filter(source=source)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["statuses"] = LeadStatus.choices
        return ctx


class LeadDetailView(LoginRequiredMixin, DetailView):
    model = Lead
    template_name = "leads/lead_detail.html"
    context_object_name = "lead"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["activity_form"] = LeadActivityForm()
        ctx["activities"] = self.object.activities.all()
        return ctx


class LeadCreateView(LoginRequiredMixin, AuditMixin, CreateView):
    model = Lead
    form_class = LeadForm
    template_name = "leads/lead_form.html"

    def get_success_url(self):
        return self.object.get_absolute_url()


class LeadUpdateView(LoginRequiredMixin, AuditMixin, UpdateView):
    model = Lead
    form_class = LeadForm
    template_name = "leads/lead_form.html"


class LeadDeleteView(LoginRequiredMixin, DeleteView):
    model = Lead
    template_name = "leads/lead_confirm_delete.html"
    success_url = reverse_lazy("leads:list")


def lead_add_activity(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    if request.method == "POST":
        form = LeadActivityForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.lead = lead
            activity.created_by = request.user
            activity.save()
            messages.success(request, "Activity logged.")
    return redirect(lead.get_absolute_url())


def lead_convert_to_customer(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    if lead.converted_customer:
        messages.info(request, "This lead has already been converted.")
        return redirect(lead.converted_customer.get_absolute_url())

    if request.method == "POST":
        form = LeadConvertForm(request.POST)
        if form.is_valid():
            customer = Customer.objects.create(
                full_name=lead.full_name,
                company_name=lead.company,
                phone=lead.phone,
                email=lead.email,
                address_line1=lead.address,
                city=lead.city,
                created_by=request.user,
                updated_by=request.user,
            )
            if form.cleaned_data.get("create_project"):
                Project.objects.create(
                    customer=customer,
                    name=form.cleaned_data.get("project_name") or f"{lead.get_product_interest_display()} Project",
                    site_address=form.cleaned_data.get("site_address") or lead.address,
                    created_by=request.user,
                    updated_by=request.user,
                )
            lead.converted_customer = customer
            lead.status = LeadStatus.WON
            lead.save()
            messages.success(request, "Lead converted to customer.")
            return redirect(customer.get_absolute_url())
    else:
        form = LeadConvertForm(initial={"project_name": f"{lead.get_product_interest_display()} Project"})

    return render(request, "leads/lead_convert.html", {"lead": lead, "form": form})
