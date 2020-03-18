from django.urls import include, path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('register/', views.MicroRegistrationView.as_view(), name='microinvoice_register'),
    path('login/', views.MicroLoginView.as_view(), name='microinvoice_login'),
    path('logout/', auth_views.LogoutView.as_view(), name='microinvoice_logout'),
    path('profile/', views.ProfileView.as_view(), name='microinvoice_profile'),
    path('profile/fiscal/', views.FiscalEntityView.as_view(), name='microinvoice_fiscal_entity'),
    path('', views.QuickView.as_view(), name='index'),
]
