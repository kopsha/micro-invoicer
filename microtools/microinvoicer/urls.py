from django.urls import include, path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path("register/", views.MicroRegistrationView.as_view(), name="microinvoicer_register"),
    path("login/", views.MicroLoginView.as_view(), name="microinvoicer_login"),
    path("logout/", auth_views.LogoutView.as_view(), name="microinvoicer_logout"),

    path("profile", views.ProfileUpdateView.as_view(), name="profile-update"),
    path("setup", views.ProfileSetupView.as_view(), name="setup"),

    path("registry/add", views.RegistryCreateView.as_view(), name="registry-add"),
    path("registry/<int:pk>", views.RegistryUpdateView.as_view(), name="registry-update"),
    path("registry/<int:pk>/delete", views.RegistryDeleteView.as_view(), name="registry-delete"),

    path("registry/<registry_id>/contract/add", views.ContractCreateView.as_view(), name="registry-contract-add"),
    path("registry/<registry_id>/contract/<pk>", views.ContractUpdateView.as_view(), name="registry-contract-update"),
    path("registry/<registry_id>/contract/<pk>/delete", views.ContractDeleteView.as_view(), name="registry-contract-delete"),

    path("registry/<registry_id>/invoice/add", views.TimeInvoiceCreateView.as_view(), name="registry-invoice-add"),
    path("registry/<registry_id>/invoice/<pk>/detail", views.TimeInvoiceDetailView.as_view(), name="registry-invoice-detail"),
    path("registry/<registry_id>/invoice/<pk>/delete", views.TimeInvoiceDeleteView.as_view(), name="registry-invoice-delete"),
    path("registry/<registry_id>/invoice/<pk>/print", views.TimeInvoicePrintView.as_view(), name="registry-invoice-print"),

    path("home/", views.MicroHomeView.as_view(), name="home"),
    path("", views.IndexView.as_view(), name="index"),
]
