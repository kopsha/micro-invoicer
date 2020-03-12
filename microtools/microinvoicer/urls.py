from django.urls import include, path

from . import views

urlpatterns = [
    path('accounts/register/', views.MicroRegistrationView.as_view(success_url='/profile/'), name='account_registry'),
    path('accounts/', include('django_registration.backends.one_step.urls')),
    #path('accounts/', include('django.contrib.auth.urls')),
    path('', views.index, name='index'),
]
