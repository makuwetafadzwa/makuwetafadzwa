from django.urls import path

from . import views

app_name = "inventory"

urlpatterns = [
    # Suppliers
    path("suppliers/", views.SupplierListView.as_view(), name="supplier_list"),
    path("suppliers/new/", views.SupplierCreateView.as_view(), name="supplier_create"),
    path("suppliers/<int:pk>/", views.SupplierDetailView.as_view(), name="supplier_detail"),
    path("suppliers/<int:pk>/edit/", views.SupplierUpdateView.as_view(), name="supplier_edit"),
    path("suppliers/<int:pk>/delete/", views.SupplierDeleteView.as_view(), name="supplier_delete"),

    # Products
    path("", views.ProductListView.as_view(), name="product_list"),
    path("new/", views.ProductCreateView.as_view(), name="product_create"),
    path("<int:pk>/", views.ProductDetailView.as_view(), name="product_detail"),
    path("<int:pk>/edit/", views.ProductUpdateView.as_view(), name="product_edit"),
    path("<int:pk>/delete/", views.ProductDeleteView.as_view(), name="product_delete"),
    path("<int:pk>/adjust/", views.adjust_stock, name="adjust_stock"),

    # Categories
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    path("categories/new/", views.CategoryCreateView.as_view(), name="category_create"),
    path("categories/<int:pk>/edit/", views.CategoryUpdateView.as_view(), name="category_edit"),
    path("categories/<int:pk>/delete/", views.CategoryDeleteView.as_view(), name="category_delete"),

    # Purchase Orders
    path("purchase-orders/", views.PurchaseOrderListView.as_view(), name="po_list"),
    path("purchase-orders/new/", views.PurchaseOrderCreateView.as_view(), name="po_create"),
    path("purchase-orders/<int:pk>/", views.PurchaseOrderDetailView.as_view(), name="po_detail"),
    path("purchase-orders/<int:pk>/edit/", views.PurchaseOrderUpdateView.as_view(), name="po_edit"),
    path("purchase-orders/<int:pk>/delete/", views.PurchaseOrderDeleteView.as_view(), name="po_delete"),
    path("purchase-orders/<int:pk>/lines/", views.manage_po_lines, name="po_lines"),
    path("purchase-orders/<int:pk>/receive/", views.receive_purchase_order, name="po_receive"),
]
