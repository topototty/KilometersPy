import datetime
import logging
import os
import random
import json
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.core.checks import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from KilometersApp.models import CargoType, Check, Order, Profile, VehicleType, OrderStatus
from django.views.decorators.csrf import csrf_exempt
from django.db.utils import IntegrityError
from django.contrib.auth import user_logged_in, user_logged_out
from django.template.loader import render_to_string
import io
import tempfile
import weasyprint


logger = logging.getLogger(__name__)

def HomeNavigation(request):
    vehicle_types = VehicleType.objects.all()
    cargo_types = CargoType.objects.all()  # Добавляем типы грузов
    return render(request, "index.html", {
        'vehicle_types': vehicle_types,
        'cargo_types': cargo_types,  # Передаем в шаблон
    })


@login_required
def create_order(request):
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        try:
            # Получение данных
            origin_address = request.POST.get("origin_address")
            destination_address = request.POST.get("destination_address")
            origin_coordinates = request.POST.get("origin_coordinates")
            destination_coordinates = request.POST.get("destination_coordinates")
            cargo_width = request.POST.get("cargo_width")
            cargo_length = request.POST.get("cargo_length")
            cargo_weight = request.POST.get("cargo_weight")
            cargo_type_id = request.POST.get("cargo_type")
            cargo_description = request.POST.get("cargo_description")
            delivery_date = request.POST.get("delivery_date")
            delivery_time = request.POST.get("delivery_time")
            selected_vehicle_id = request.POST.get("selected_vehicle_id")

            # Проверка наличия всех данных
            if not all([origin_address, destination_address, origin_coordinates, destination_coordinates,
                        cargo_width, cargo_length, cargo_weight, cargo_type_id, cargo_description,
                        delivery_date, delivery_time, selected_vehicle_id]):
                return JsonResponse({"success": False, "message": "Все поля должны быть заполнены."})

            # Преобразование числовых значений с обработкой ошибок
            try:
                cargo_width = float(cargo_width)
                cargo_length = float(cargo_length)
                cargo_weight = float(cargo_weight)
            except ValueError:
                return JsonResponse({"success": False, "message": "Некорректные данные о габаритах груза."})

            # Получение ТС и типа груза
            vehicle = VehicleType.objects.get(pk=selected_vehicle_id)
            cargo_type = CargoType.objects.get(pk=cargo_type_id)

            # Проверка характеристик груза
            if cargo_width > vehicle.max_width or \
               cargo_length > vehicle.max_length or \
               cargo_weight > vehicle.max_weight:
                return JsonResponse({"success": False, "message": "Груз превышает допустимые параметры."})

            # Статус заказа по умолчанию
            default_status, _ = OrderStatus.objects.get_or_create(name="Ожидание")

            # Генерация уникального номера заказа
            while True:
                try:
                    order_number = f"{random.randint(1000000, 9999999)}"
                    order = Order.objects.create(
                        origin_address=origin_address,
                        destination_address=destination_address,
                        origin_coordinates=origin_coordinates,
                        destination_coordinates=destination_coordinates,
                        cargo_width=cargo_width,
                        cargo_length=cargo_length,
                        cargo_weight=cargo_weight,
                        cargo_description=cargo_description,
                        delivery_date=delivery_date,
                        delivery_time=delivery_time,
                        user_id=request.user,
                        cargo_type=cargo_type,
                        vehicle_type=vehicle,
                        order_status=default_status,
                        order_number=order_number
                    )
                    order.create_check()
                    break
                except IntegrityError:
                    continue

            return JsonResponse({
                "success": True,
                "order_id": order.pk,
                "origin_address": order.origin_address,
                "destination_address": order.destination_address,
                "price": float(vehicle.price),
            })

        except VehicleType.DoesNotExist:
            return JsonResponse({"success": False, "message": "Выбранное транспортное средство не существует."})
        except CargoType.DoesNotExist:
            return JsonResponse({"success": False, "message": "Выбранный тип груза не существует."})
        except Exception as e:
            logger.error(f"Произошла ошибка: {e}")
            return JsonResponse({"success": False, "message": f"Произошла ошибка на сервере. {e}"}, status=500)

    return JsonResponse({"success": False, "message": "Некорректный запрос."}, status=400)


@login_required
def my_orders(request):
    user = request.user

    # Получаем заказы пользователя
    user_orders = Order.objects.filter(user_id=user)

    # Предполагается, что в статусах заказов есть следующие названия:
    # Для "Активных" - "Доставляется" или "Ожидание"
    active_statuses = ["Доставляется", "Ожидание"]
    # Для "Завершенных" - "Выполнен" или "Доставлен"
    done_statuses = ["Выполнен", "Доставлен"]
    # Для "Отмененных" - "Отменен"
    canceled_statuses = ["Отменен"]

    active_orders = user_orders.filter(order_status__name__in=active_statuses)
    done_orders = user_orders.filter(order_status__name__in=done_statuses)
    canceled_orders = user_orders.filter(order_status__name__in=canceled_statuses)

    return render(request, 'User/my_orders.html', {
        'active_orders': active_orders,
        'done_orders': done_orders,
        'canceled_orders': canceled_orders
    })


@login_required
def profile_view(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    
    # Получаем ближайший заказ
    nearest_order = Order.objects.filter(user_id=user).order_by('delivery_date', 'delivery_time').first()
    
    # Получаем группы пользователя
    user_groups = user.groups.values_list('name', flat=True)
    
    return render(request, 'User/profile.html', {
        'user': user,
        'profile': profile,
        'nearest_order': nearest_order,
        'user_groups': user_groups,  # Передаем группы пользователя в шаблон
    })

@login_required
def checks_view(request):
    user = request.user
    # Сортируем по дате и времени (новые сверху)
    checks = Check.objects.filter(user_id=user).order_by('-date', '-time')
    return render(request, 'User/checks.html', {
        'checks': checks
    })


@login_required
def check_pdf_view(request, pk):
    # Получаем объект чек
    check = get_object_or_404(Check, pk=pk)
    
    # Рендерим HTML контент с данными чека
    html_content = render_to_string('User/check_pdf.html', {'check': check})
    
    # Генерация PDF из HTML с использованием WeasyPrint
    pdf_file = weasyprint.HTML(string=html_content).write_pdf()

    # Возвращаем PDF как ответ с нужными заголовками
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="check_{check.order.order_number}.pdf"'
    return response