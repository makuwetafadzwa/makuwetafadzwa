from decimal import Decimal

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
from .forms import (
    ProductCategoryForm,
    ProductForm,
    PurchaseOrderForm,
    PurchaseOrderLineFormSet,
    StockAdjustmentForm,
    SupplierForm,
)
from .models import (
    Product,
    ProductCategory,
    PurchaseOrder,
    PurchaseOrderStatus,
    StockMovement,
    Supplier,
)


# --------------- Suppliers ---------------
class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    template_name = "inventory/supplier_list.html"
    context_object_name = "suppliers"
    paginate_by = 20


class SupplierDetailView(LoginRequiredMixin, DetailView):
    model = Supplier
    template_name = "inventory/supplier_detail.html"
    context_object_name = "supplier"


class SupplierCreateView(LoginRequiredMixin, AuditMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = "inventory/supplier_form.html"
    success_url = reverse_lazy("inventory:supplier_list")


class SupplierUpdateView(LoginRequiredMixin, AuditMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = "inventory/supplier_form.html"
    success_url = reverse_lazy("inventory:supplier_list")


class SupplierDeleteView(LoginRequiredMixin, DeleteView):
    model = Supplier
    template_name = "inventory/supplier_confirm_delete.html"
    success_url = reverse_lazy("inventory:supplier_list")


# --------------- Products ---------------
class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = "inventory/product_list.html"
    context_object_name = "products"
    paginate_by = 30

    def get_queryset(self):
        qs = super().get_queryset().select_related("category", "preferred_supplier")
        q = self.request.GET.get("q")
        category = self.request.GET.get("category")
        low = self.request.GET.get("low")
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(sku__icontains=q))
        if category:
            qs = qs.filter(category_id=category)
        if low:
            qs = [p for p in qs if p.is_low_stock]
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = ProductCategory.objects.all()
        return ctx


class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = "inventory/product_detail.html"
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["movements"] = self.object.movements.all()[:50]
        ctx["adjust_form"] = StockAdjustmentForm()
        return ctx


class ProductCreateView(LoginRequiredMixin, AuditMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "inventory/product_form.html"
    success_url = reverse_lazy("inventory:product_list")


class ProductUpdateView(LoginRequiredMixin, AuditMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "inventory/product_form.html"
    success_url = reverse_lazy("inventory:product_list")


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = "inventory/product_confirm_delete.html"
    success_url = reverse_lazy("inventory:product_list")


def adjust_stock(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = StockAdjustmentForm(request.POST)
        if form.is_valid():
            product.adjust_stock(
                Decimal(form.cleaned_data["change"]),
                reason=form.cleaned_data["reason"],
                user=request.user,
                reference=form.cleaned_data.get("reference", ""),
            )
            messages.success(request, "Stock adjusted.")
    return redirect(product.get_absolute_url())


# --------------- Categories ---------------
class CategoryListView(LoginRequiredMixin, ListView):
    model = ProductCategory
    template_name = "inventory/category_list.html"
    context_object_name = "categories"


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = ProductCategory
    form_class = ProductCategoryForm
    template_name = "inventory/category_form.html"
    success_url = reverse_lazy("inventory:category_list")


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = ProductCategory
    form_class = ProductCategoryForm
    template_name = "inventory/category_form.html"
    success_url = reverse_lazy("inventory:category_list")


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = ProductCategory
    template_name = "inventory/category_confirm_delete.html"
    success_url = reverse_lazy("inventory:category_list")


# --------------- Purchase Orders ---------------
class PurchaseOrderListView(LoginRequiredMixin, ListView):
    model = PurchaseOrder
    template_name = "inventory/po_list.html"
    context_object_name = "purchase_orders"
    paginate_by = 20


class PurchaseOrderDetailView(LoginRequiredMixin, DetailView):
    model = PurchaseOrder
    template_name = "inventory/po_detail.html"
    context_object_name = "po"


class PurchaseOrderCreateView(LoginRequiredMixin, AuditMixin, CreateView):
    model = PurchaseOrder
    form_class = PurchaseOrderForm
    template_name = "inventory/po_form.html"

    def get_success_url(self):
        return reverse_lazy("inventory:po_lines", args=[self.object.pk])


class PurchaseOrderUpdateView(LoginRequiredMixin, AuditMixin, UpdateView):
    model = PurchaseOrder
    form_class = PurchaseOrderForm
    template_name = "inventory/po_form.html"

    def get_success_url(self):
        return reverse_lazy("inventory:po_detail", args=[self.object.pk])


class PurchaseOrderDeleteView(LoginRequiredMixin, DeleteView):
    model = PurchaseOrder
    template_name = "inventory/po_confirm_delete.html"
    success_url = reverse_lazy("inventory:po_list")


def manage_po_lines(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == "POST":
        formset = PurchaseOrderLineFormSet(request.POST, instance=po)
        if formset.is_valid():
            formset.save()
            messages.success(request, "Purchase order lines saved.")
            return redirect(po.get_absolute_url())
    else:
        formset = PurchaseOrderLineFormSet(instance=po)
    return render(request, "inventory/po_lines.html", {"po": po, "formset": formset})


def receive_purchase_order(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    if po.status == PurchaseOrderStatus.RECEIVED:
        messages.info(request, "Purchase order already received.")
        return redirect(po.get_absolute_url())

    for line in po.lines.all():
        outstanding = line.outstanding
        if outstanding > 0:
            line.product.adjust_stock(
                outstanding,
                reason="purchase",
                user=request.user,
                reference=po.po_number,
            )
            line.received_quantity = line.quantity
            line.save()

    po.status = PurchaseOrderStatus.RECEIVED
    po.updated_by = request.user
    po.save()
    messages.success(request, "Stock received and inventory updated.")
    return redirect(po.get_absolute_url())
