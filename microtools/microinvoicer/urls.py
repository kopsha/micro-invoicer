from django.urls import include, path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('register/', views.MicroRegistrationView.as_view(), name='microinvoicer_register'),
    path('login/', views.MicroLoginView.as_view(), name='microinvoicer_login'),
    path('logout/', auth_views.LogoutView.as_view(), name='microinvoicer_logout'),
    path('profile/', views.ProfileView.as_view(), name='microinvoicer_profile'),
    path('setup/', views.SellerView.as_view(), name='microinvoicer_setup'),
    path('contract/', views.ContractView.as_view(), name='microinvoicer_contract'),
    path('contracts/', views.ContractsView.as_view(), name='microinvoicer_contracts'),
    path('draft_time/', views.DraftInvoiceView.as_view(), name='microinvoicer_draft_time'),
    path('draft_material/', views.DraftInvoiceView.as_view(), name='microinvoicer_draft_material'),
    path('time_invoice/<invoice_id>', views.TimeInvoiceView.as_view(), name='microinvoicer_time_invoice'),
    path('home/', views.MicroHomeView.as_view(), name='microinvoicer_home'),
    path('', views.IndexView.as_view(), name='index'),
]
