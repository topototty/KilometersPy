from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse
from django_tables2 import RequestConfig
from KilometersApp.Admin.filters import OrderFilter, RouteFilter
from KilometersApp.Admin.forms import RouteForm
from KilometersApp.models import Order, Route
from KilometersApp.Admin.tables import OrderTable, RouteTable
from django.contrib.auth.decorators import login_required

@login_required
def orders_view(request):
    orders = Order.objects.all()
    order_filter = OrderFilter(request.GET, queryset=orders)  # Применяем фильтрацию
    orders_table = OrderTable(order_filter.qs)
    return render(request, "Manager/orders.html", 
                  {"orders_table": orders_table,
                   'filter': order_filter,
                   })


@login_required
def order_details(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return JsonResponse({
        "order_number": order.order_number,
        "origin_address": order.origin_address,
        "destination_address": order.destination_address,
        "origin_coordinates": order.origin_coordinates,
        "destination_coordinates": order.destination_coordinates,
        "cargo_width": order.cargo_width,
        "cargo_length": order.cargo_length,
        "cargo_weight": order.cargo_weight,
        "cargo_description": order.cargo_description,
        "delivery_date": order.delivery_date.strftime('%Y-%m-%d'),
        "delivery_time": order.delivery_time.strftime('%H:%M'),
    })


def route_list(request):
    # Фильтр маршрутов
    routes = Route.objects.all()
    route_filter = RouteFilter(request.GET, queryset=routes)
    table = RouteTable(route_filter.qs)

    # Подключение фильтров к таблице
    RequestConfig(request).configure(table)

    # Обработка добавления нового маршрута
    if request.method == "POST":
        form = RouteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('route_list')  # Перенаправление на список маршрутов после добавления
    else:
        form = RouteForm()

    return render(request, 'Manager/routes_list.html', {
        'filter': route_filter,
        'table': table,
        'form': form,
    })