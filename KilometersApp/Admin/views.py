import os
import matplotlib
from django.core.management import call_command

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
from django.db.models import Count
from django.shortcuts import redirect, render
from django.views import View
from django_filters.views import FilterView
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django_tables2.views import SingleTableMixin
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.db.models import Count

from KilometersApp.Admin.filters import *
from KilometersApp.Admin.forms import *
from KilometersApp.Admin.tables import *


def admin_panel(request):
    tabs = [
        # User
        {
            "model_name": UserProxy._meta.model_name,
            "title": "Пользователи",
            "verbose_name_plural": UserProxy._meta.verbose_name_plural,
            "table": UserTable(UserFilter(request.GET, queryset=UserProxy.objects.all()).qs, request=request),
            "filter": UserFilter(request.GET, queryset=UserProxy.objects.all()),
            "model": UserProxy,
        },

        # Order
        {
            "model_name": Order._meta.model_name,
            "title": "Заказы",
            "verbose_name_plural": Order._meta.verbose_name_plural,
            "table": OrderTable(OrderFilter(request.GET, queryset=Order.objects.all()).qs, request=request),
            "filter": OrderFilter(request.GET, queryset=Order.objects.all()),
            "model": Order,
        },
        # CargoType
        {
            "model_name": CargoType._meta.model_name,
            "title": "Типы грузов",
            "verbose_name_plural": CargoType._meta.verbose_name_plural,
            "table": CargoTypeTable(CargoTypeFilter(request.GET, queryset=CargoType.objects.all()).qs, request=request),
            "filter": CargoTypeFilter(request.GET, queryset=CargoType.objects.all()),
            "model": CargoType,
        },
        # OrderStatus
        {
            "model_name": OrderStatus._meta.model_name,
            "title": "Статусы заказов",
            "verbose_name_plural": OrderStatus._meta.verbose_name_plural,
            "table": OrderStatusTable(OrderStatusFilter(request.GET, queryset=OrderStatus.objects.all()).qs,
                                      request=request),
            "filter": OrderStatusFilter(request.GET, queryset=OrderStatus.objects.all()),
            "model": OrderStatus,
        },
        # Route
        {
            "model_name": Route._meta.model_name,
            "title": "Маршруты",
            "verbose_name_plural": Route._meta.verbose_name_plural,
            "table": RouteTable(RouteFilter(request.GET, queryset=Route.objects.all()).qs, request=request),
            "filter": RouteFilter(request.GET, queryset=Route.objects.all()),
            "model": Route,
        },
        # Driver
        {
            "model_name": Driver._meta.model_name,
            "title": "Водители",
            "verbose_name_plural": Driver._meta.verbose_name_plural,
            "table": DriverTable(DriverFilter(request.GET, queryset=Driver.objects.all()).qs, request=request),
            "filter": DriverFilter(request.GET, queryset=Driver.objects.all()),
            "model": Driver,
        },

        # Vehicle
        {
            "model_name": Vehicle._meta.model_name,
            "title": "Транспортные средства",
            "verbose_name_plural": Vehicle._meta.verbose_name_plural,
            "table": VehicleTable(VehicleFilter(request.GET, queryset=Vehicle.objects.all()).qs, request=request),
            "filter": VehicleFilter(request.GET, queryset=Vehicle.objects.all()),
            "model": Vehicle,
        },
        # VehicleStatus
        {
            "model_name": VehicleStatus._meta.model_name,
            "title": "Статусы ТС",
            "verbose_name_plural": VehicleStatus._meta.verbose_name_plural,
            "table": VehicleStatusTable(VehicleStatusFilter(request.GET, queryset=VehicleStatus.objects.all()).qs,
                                        request=request),
            "filter": VehicleStatusFilter(request.GET, queryset=VehicleStatus.objects.all()),
            "model": VehicleStatus,
        },
        # Trailer
        {
            "model_name": Trailer._meta.model_name,
            "title": "Прицепы",
            "verbose_name_plural": Trailer._meta.verbose_name_plural,
            "table": TrailerTable(TrailerFilter(request.GET, queryset=Trailer.objects.all()).qs, request=request),
            "filter": TrailerFilter(request.GET, queryset=Trailer.objects.all()),
            "model": Trailer,
        },

        # VehicleType
        {
            "model_name": VehicleType._meta.model_name,
            "title": "Типы ТС",
            "verbose_name_plural": VehicleType._meta.verbose_name_plural,
            "table": VehicleTypeTable(VehicleTypeFilter(request.GET, queryset=VehicleType.objects.all()).qs,
                                      request=request),
            "filter": VehicleTypeFilter(request.GET, queryset=VehicleType.objects.all()),
            "model": VehicleType,
        },
    ]
    for tab in tabs:
        model_name = tab["model"]._meta.model_name
        app_label = tab["model"]._meta.app_label
        tab["can_add"] = request.user.has_perm(f"{app_label}.add_{model_name}")
        tab["can_change"] = request.user.has_perm(f"{app_label}.change_{model_name}")
        tab["can_delete"] = request.user.has_perm(f"{app_label}.delete_{model_name}")

    # Фильтруем вкладки по правам пользователя
    tabs = [
        tab for tab in tabs
        if request.user.has_perm(f"{tab['model']._meta.app_label}.view_{tab['model']._meta.model_name}")
    ]

    return render(request, "Admin/admin_panel.html", {"tabs": tabs})


class BaseCreateView(SuccessMessageMixin, CreateView):
    template_name = "inc/form.html"
    success_message = _("Объект успешно создан")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Добавить {self.model._meta.verbose_name}"
        # Передача модели для генерации ссылки
        context['object'] = self.model()
        return context

    def get_success_url(self):
        """
        Использует get_list_url объекта для перенаправления.
        """
        if hasattr(self.object, 'get_list_url'):
            return self.object.get_list_url()
        return reverse_lazy("admin_panel")


class BaseUpdateView(SuccessMessageMixin, UpdateView):
    template_name = "inc/form.html"
    success_message = _("Объект успешно обновлен")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Редактировать {self.model._meta.verbose_name}"
        # Передача модели для генерации ссылки
        context['object'] = self.model()
        return context

    def get_success_url(self):
        """
        Использует get_list_url объекта для перенаправления.
        """
        if hasattr(self.object, 'get_list_url'):
            return self.object.get_list_url()
        return reverse_lazy("admin_panel")


class BaseDeleteView(SuccessMessageMixin, DeleteView):
    template_name = "inc/delete_confirm.html"
    success_message = _("Объект успешно удален")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Удалить {self.model._meta.verbose_name}"
        # Передача модели для генерации ссылки
        context['object'] = self.model()
        return context

    def get_success_url(self):
        """
        Использует get_list_url объекта для перенаправления.
        """
        if hasattr(self.object, 'get_list_url'):
            return self.object.get_list_url()
        return reverse_lazy("admin_panel")


# User Views
class UserCreateView(BaseCreateView):
    model = User
    form_class = UserForm


class UserUpdateView(BaseUpdateView):
    model = User
    form_class = UserForm


class UserDeleteView(BaseDeleteView):
    model = User


# Order Views
class OrderCreateView(BaseCreateView):
    model = Order
    form_class = OrderForm


class OrderUpdateView(BaseUpdateView):
    model = Order
    form_class = OrderForm


class OrderDeleteView(BaseDeleteView):
    model = Order


# CargoType Views
class CargoTypeCreateView(BaseCreateView):
    model = CargoType
    form_class = CargoTypeForm


class CargoTypeUpdateView(BaseUpdateView):
    model = CargoType
    form_class = CargoTypeForm


class CargoTypeDeleteView(BaseDeleteView):
    model = CargoType


class OrderStatusCreateView(BaseCreateView):
    model = OrderStatus
    form_class = OrderStatusForm


class OrderStatusUpdateView(BaseUpdateView):
    model = OrderStatus
    form_class = OrderStatusForm


class OrderStatusDeleteView(BaseDeleteView):
    model = OrderStatus


# Route Views
class RouteCreateView(BaseCreateView):
    model = Route
    form_class = RouteForm


class RouteUpdateView(BaseUpdateView):
    model = Route
    form_class = RouteForm


class RouteDeleteView(BaseDeleteView):
    model = Route


# Driver Views
class DriverCreateView(BaseCreateView):
    model = Driver
    form_class = DriverForm


class DriverUpdateView(BaseUpdateView):
    model = Driver
    form_class = DriverForm


class DriverDeleteView(BaseDeleteView):
    model = Driver


# Vehicle Views
class VehicleCreateView(BaseCreateView):
    model = Vehicle
    form_class = VehicleForm


class VehicleUpdateView(BaseUpdateView):
    model = Vehicle
    form_class = VehicleForm


class VehicleDeleteView(BaseDeleteView):
    model = Vehicle


# VehicleStatus Views
class VehicleStatusCreateView(BaseCreateView):
    model = VehicleStatus
    form_class = VehicleStatusForm


class VehicleStatusUpdateView(BaseUpdateView):
    model = VehicleStatus
    form_class = VehicleStatusForm


class VehicleStatusDeleteView(BaseDeleteView):
    model = VehicleStatus


# Trailer Views
class TrailerCreateView(BaseCreateView):
    model = Trailer
    form_class = TrailerForm


class TrailerUpdateView(BaseUpdateView):
    model = Trailer
    form_class = TrailerForm


class TrailerDeleteView(BaseDeleteView):
    model = Trailer


# VehicleType Views
class VehicleTypeCreateView(BaseCreateView):
    model = VehicleType
    form_class = VehicleTypeForm


class VehicleTypeUpdateView(BaseUpdateView):
    model = VehicleType
    form_class = VehicleTypeForm


class VehicleTypeDeleteView(BaseDeleteView):
    model = VehicleType


BACKUP_DIR = os.path.join(settings.BASE_DIR, "backups")


def get_backup_files():
    """Возвращает список файлов из папки с бэкапами."""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    return [f for f in os.listdir(BACKUP_DIR) if f.endswith('.json')]


class BackupListView(View):
    def get(self, request):
        """Отображение списка бэкапов."""
        files = get_backup_files()
        return render(request, "admin/backup_list.html", {"backup_files": files})


class BackupRestoreView(View):
    def post(self, request, filename):
        """Восстановление бэкапа только для конкретного приложения."""
        app_name = "KilometersApp"  # Укажите имя вашего приложения здесь
        backup_path = os.path.join(BACKUP_DIR, filename)

        if not os.path.exists(backup_path):
            messages.error(request, f"Файл {filename} не найден.", extra_tags="backup")
            return redirect("backup_list")
        try:
            # Восстановление данных только для указанного приложения
            call_command('loaddata', backup_path)
            messages.success(request, f"Данные из {filename} успешно восстановлены для приложения {app_name}.",
                             extra_tags="backup")
        except Exception as e:
           print(f"Ошибка восстановления: {e}")

        return redirect("backup_list")


class BackupDeleteView(View):
    def post(self, request, filename):
        """Удаление бэкапа."""
        backup_path = os.path.join(BACKUP_DIR, filename)
        if os.path.exists(backup_path):
            os.remove(backup_path)
            messages.success(request, f"Бэкап {filename} успешно удален.", extra_tags="backup")
        else:
            messages.error(request, f"Файл {filename} не найден.", extra_tags="backup")
        return redirect("backup_list")


class BackupCreateView(View):
    def post(self, request):
        """Создание нового бэкапа только для конкретного приложения."""
        app_name = "KilometersApp"  # Укажите имя вашего приложения здесь

        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)

        filename = f"backup_{timezone.now().strftime('%Y%m%d_%H%M%S')}.json"
        backup_path = os.path.join(BACKUP_DIR, filename)

        try:
            # Создание бэкапа только для указанного приложения
            os.system(f'python manage.py dumpdata {app_name} --indent 2 -o {backup_path}')
            messages.success(request, f"Бэкап {filename} успешно создан для приложения {app_name}.",
                             extra_tags="backup")
        except Exception as e:
            messages.error(request, f"Ошибка при создании бэкапа: {e}", extra_tags="backup")

        return redirect("backup_list")


class UserActionLogListView(SingleTableMixin, FilterView):
    model = UserActionLog
    table_class = UserActionLogTable  # Используем таблицу для отображения логов
    filterset_class = UserActionLogFilter  # Используем фильтр для логов
    template_name = "admin/user_action_log_list.html"  # Шаблон для отображения
    paginate_by = 20  # Количество записей на странице


def orders_stats_view(request):
    # Получаем количество заказов, сгруппированных по дате доставки
    orders = Order.objects.values('delivery_date').annotate(count=Count('pk')).order_by('delivery_date')

    # Преобразуем в DataFrame для удобной обработки
    data = pd.DataFrame(list(orders))

    # Проверяем, есть ли данные. Если нет, создаем пустую таблицу
    if 'delivery_date' not in data.columns or 'count' not in data.columns:
        data = pd.DataFrame(columns=['delivery_date', 'count'])

    # Преобразуем даты в формат datetime.date
    if not data.empty:
        data['delivery_date'] = pd.to_datetime(data['delivery_date']).dt.date

    # Заполняем пропуски для всех дней в диапазоне дат
    if not data.empty:
        start_date = data['delivery_date'].min()
        end_date = data['delivery_date'].max()
    else:
        start_date = date.today()
        end_date = date.today()

    full_range = pd.date_range(start=start_date, end=end_date)
    full_data = pd.DataFrame({'delivery_date': full_range.date})
    data = full_data.merge(data, on='delivery_date', how='left').fillna(0)

    # Преобразуем количество заказов к целочисленному типу
    data['count'] = data['count'].astype(int)

    # Создаем график
    plt.figure(figsize=(12, 6))
    plt.bar(data['delivery_date'], data['count'], color='skyblue', width=0.1)
    plt.title("Количество заказов по дням", fontsize=16)
    plt.xlabel("Дата доставки", fontsize=14)
    plt.ylabel("Количество заказов", fontsize=14)
    # Настраиваем форматирование оси X
    plt.xticks(ticks=data['delivery_date'], labels=[date.strftime('%Y-%m-%d') for date in data['delivery_date']], rotation=45)
    plt.tight_layout()  # Убираем наложение элементов

    

    # Конвертируем график в изображение для отображения на веб-странице
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    return render(request, 'admin/stats.html', {'chart': image_base64})