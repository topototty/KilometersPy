from django.shortcuts import render, redirect, get_object_or_404
from KilometersApp.models import Order, OrderStatus


def driver_dashboard(request):
    driver = request.user.driver 

    if request.method == "POST":
        # Получаем заказ и новый статус из POST-запроса
        order_id = request.POST.get('order_id')
        new_status_name = request.POST.get('new_status')

        # Получаем или создаем статус с таким именем (если его нет)
        new_status, created = OrderStatus.objects.get_or_create(name=new_status_name)

        # Обновляем статус заказа
        order = get_object_or_404(Order, pk=order_id, route__driver_id=driver)
        order.order_status = new_status  # Обновляем статус на новый
        order.save()  # Сохраняем изменения
        return redirect('driver_dashboard')

    # Получаем заказы, связанные с водителем
    orders = Order.objects.filter(route__driver_id=driver).distinct()

    # Разбиваем заказы по статусу
    orders_by_status = {
        "Ожидание": orders.filter(order_status__name="Ожидание"),
        "Доставляется": orders.filter(order_status__name="Доставляется"),
        "Доставлен": orders.filter(order_status__name="Доставлен"),
        "Отменен": orders.filter(order_status__name="Отменен"),
    }

    return render(request, 'Driver/driver_dashboard.html', {
        'orders_by_status': orders_by_status,
    })
