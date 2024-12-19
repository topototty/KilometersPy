from django.urls import path, include
from django.views.generic import TemplateView


from KilometersApp.User.views import *

urlpatterns = [
    path('', HomeNavigation, name="home"),
    path('auth/', include('KilometersApp.Auth.urls')),
    path('managment/', include('KilometersApp.Admin.urls')),
    path('managment/', include('KilometersApp.Manager.urls')),
    path('driver/', include('KilometersApp.Driver.urls')),

    path('create_order/', create_order, name='create_order'),
    path('orders/', my_orders, name='my_orders'),
    path('profile/', profile_view, name='profile'),
    path('checks/', checks_view, name='checks'),
    path('checks/pdf/<int:pk>/', check_pdf_view, name='check_pdf'),
    path('license/', TemplateView.as_view(template_name='user/license.html'), name='license'),
]
