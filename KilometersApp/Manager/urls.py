from django.urls import path
from KilometersApp.Manager.views import orders_view, order_details, route_list

urlpatterns = [
    path('orders/', orders_view, name='orders'),
    path('orders/<int:order_id>/details/', order_details, name='order_details'),
    path('routes/', route_list, name='route_list'),
]
