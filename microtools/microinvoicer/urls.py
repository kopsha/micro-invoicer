from django.urls import include, path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('register/', views.MicroRegistrationView.as_view(), name='microinvoice_register'),
    path('login/', views.MicroLoginView.as_view(), name='microinvoice_login'),
    path('logout/', auth_views.LogoutView.as_view(), name='microinvoice_logout'),
    path('profile/', views.ProfileView.as_view(), name='microinvoice_profile'),
    path('profile/fiscal/', views.SellerView.as_view(), name='microinvoice_fiscal_entity'),
    path('setup/', views.SellerView.as_view(), name='microinvoice_setup'),
    path('buyer/', views.BuyerView.as_view(), name='microinvoice_buyer'),
    path('contracts/', views.ContractsView.as_view(), name='microinvoice_contracts'),
    path('draft_time/', views.DraftInvoiceView.as_view(), name='microinvoice_draft_time'),
    path('draft_material/', views.DraftInvoiceView.as_view(), name='microinvoice_draft_material'),
    path('', views.MicroHomeView.as_view(), name='index'),
]
