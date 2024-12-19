from django.urls import path, include
from .views import driver_dashboard


urlpatterns = [
    path('dashboard/', driver_dashboard, name='driver_dashboard'),
]
