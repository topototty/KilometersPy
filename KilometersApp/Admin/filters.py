from django import forms
import django_filters
from django.contrib.auth.models import User

from KilometersApp.models import *


class BaseFilterSet(django_filters.FilterSet):
    """
    Базовый класс для фильтров, добавляет стили, placeholder и help_text к виджетам.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.filters.items():
            widget = field.field.widget

            # Добавляем классы для различных типов виджетов
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.update({"class": "form-check-input"})
            elif isinstance(widget, forms.RadioSelect):
                widget.attrs.update({"class": "form-check-input"})  # Радио кнопки
            elif isinstance(widget, forms.Select):
                widget.attrs.update({"class": "form-select"})  # Выпадающие списки
            elif isinstance(widget, (forms.Textarea, forms.TextInput, forms.EmailInput, forms.URLInput, forms.NumberInput, forms.PasswordInput)):
                widget.attrs.update({"class": "form-control"})  # Поля ввода
            elif isinstance(widget, forms.ClearableFileInput):
                widget.attrs.update({"class": "form-control-file"})  # Файл
            elif isinstance(widget, forms.DateInput):
                widget.attrs.update({"class": "form-control datepicker"})  # Дата
            elif isinstance(widget, forms.DateTimeInput):
                widget.attrs.update({"class": "form-control datetimepicker"})  # Дата + время
            elif isinstance(widget, forms.TimeInput):
                widget.attrs.update({"class": "form-control timepicker"})  # Время
            else:
                widget.attrs.update({"class": "form-control"})  # По умолчанию


class UserFilter(BaseFilterSet):
    """
    Фильтр для пользователей с кастомной стилизацией.
        is_staff = django_filters.BooleanFilter(
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        label="Администратор"
    )
    """

    class Meta:
        model = User
        fields = ["username", "email", "is_staff"]


class OrderFilter(BaseFilterSet):
    class Meta:
        model = Order
        fields = [
            "order_number", "user_id", "cargo_type", 
            "vehicle_type", "order_status"
        ]


class CargoTypeFilter(BaseFilterSet):
    class Meta:
        model = CargoType
        fields = ["name"]

class OrderStatusFilter(BaseFilterSet):
    class Meta:
        model = OrderStatus
        fields = ["name"]

class RouteFilter(BaseFilterSet):
    class Meta:
        model = Route
        fields = ["route_number", "order_id", "driver_id", "vehicle_id"]

class DriverFilter(BaseFilterSet):
    class Meta:
        model = Driver
        fields = ["drivers_license_number", "license_categories"]

class VehicleFilter(BaseFilterSet):
    class Meta:
        model = Vehicle
        fields = ["brand", "license_plate", "vehicle_status", "vehicle_type_id"]

class VehicleStatusFilter(BaseFilterSet):
    class Meta:
        model = VehicleStatus
        fields = ["status"]

class TrailerFilter(BaseFilterSet):
    class Meta:
        model = Trailer
        fields = ["name", "vehicle_type_id"]

class VehicleTypeFilter(BaseFilterSet):
    class Meta:
        model = VehicleType
        fields = ["name"]

class UserActionLogFilter(BaseFilterSet):
    user = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        label="Пользователь",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    model_name = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Модель",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Введите имя модели"}),
    )
    action = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Действие",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Введите действие"}),
    )
    status = django_filters.ChoiceFilter(
        choices=[('INFO', 'Info'), ('ERROR', 'Error')],
        label="Статус",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = UserActionLog
        fields = ["user", "model_name", "action", "status"]
