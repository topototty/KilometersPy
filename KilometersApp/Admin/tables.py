import django_tables2 as tables
from KilometersApp.models import *
from django.utils.translation import gettext_lazy as _

class BaseTable(tables.Table):
    """
    Базовая таблица для наследования с проверкой прав
    """
    actions = tables.TemplateColumn(
        template_code='''
        {% if tab.can_change or tab.can_delete %}
        <div class="dropdown">
            <button class="btn btn-secondary btn-sm dropdown-toggle" type="button" id="dropdownMenuButton-{{ record.pk }}" data-bs-toggle="dropdown" aria-expanded="false">
                Действия
            </button>
            <ul class="dropdown-menu" aria-labelledby="dropdownMenuButton-{{ record.pk }}">
                {% if tab.can_change %}
                <li>
                    <a class="dropdown-item" href="{{ record.get_edit_url }}?current_tab={{ request.GET.current_tab }}">
                        <i class="material-icons">edit</i> Редактировать
                    </a>
                </li>
                {% endif %}
                {% if tab.can_delete %}
                <li>
                    <a class="dropdown-item text-danger" href="{{ record.get_delete_url }}?current_tab={{ request.GET.current_tab }}">
                        <i class="material-icons">delete</i> Удалить
                    </a>
                </li>
                {% endif %}
            </ul>
        </div>
        {% else %}
        ...
        {% endif %}
        ''',
        verbose_name="Действия",
        orderable=False,
        visible=True  
    )

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        model_name = kwargs.pop('model_name', None)
        super().__init__(*args, **kwargs)

        # Проверяем права и скрываем колонку "actions", если нет прав
        if request and model_name:
            can_change = request.user.has_perm(f"{model_name}.change_{model_name}")
            can_delete = request.user.has_perm(f"{model_name}.delete_{model_name}")
            if not (can_change or can_delete):
                self.base_columns['actions'].visible = False

    class Meta:
        template_name = "django_tables2/bootstrap4.html"
        empty_text = _("Нет данных для отображения.")


class UserTable(BaseTable):
    password = tables.Column(verbose_name=_("Пароль"), accessor="password", orderable=False)
    groups = tables.Column(
        verbose_name=_("Группы"),
        accessor="groups",
        orderable=False,
        default=_("Нет групп"),
    )
    phone = tables.Column(verbose_name=_("Телефон"), accessor="profile.phone", orderable=False, default=_("Не указан"))

    def render_password(self, value):
        return _("Скрыт")  # Возвращает "Скрыт" вместо хэша пароля

    def render_groups(self, value):
        return ", ".join([group.name for group in value.all()]) if value.exists() else _("Нет групп")

    class Meta(BaseTable.Meta):
        model = UserProxy
        fields = ["username", "email", "is_staff", "password", "groups", "phone"]




class ProfileTable(BaseTable):
    class Meta(BaseTable.Meta):
        model = Profile
        fields = ["user", "phone", "is_deleted"]


class OrderTable(BaseTable):
    order_number = tables.TemplateColumn(
        template_code='''
        <a href="#" class="order-detail-link" data-order-id="{{ record.pk }}" data-bs-toggle="modal" data-bs-target="#orderModal">
            {{ record.order_number }}
        </a>
        ''',
        verbose_name="Номер заказа"
    )

    class Meta(BaseTable.Meta):
        model = Order
        fields = ["order_number", "cargo_width", "cargo_length", "cargo_weight", "origin_address", "destination_address"]


class CargoTypeTable(BaseTable):
    class Meta(BaseTable.Meta):
        model = CargoType
        fields = ["name"]


class OrderStatusTable(BaseTable):
    class Meta(BaseTable.Meta):
        model = OrderStatus
        fields = ["name"]


class RouteTable(BaseTable):
    class Meta(BaseTable.Meta):
        model = Route
        fields = ["route_number", "order_id", "driver_id", "vehicle_id"]


class DriverTable(BaseTable):
    class Meta(BaseTable.Meta):
        model = Driver
        fields = ["drivers_license_number", "date_of_issue_of_drivers_license", "driving_experience"]


class DriversLicenseCategoryTypeTable(BaseTable):
    class Meta(BaseTable.Meta):
        model = DriversLicenseCategoryType
        fields = ["name", "description"]


class VehicleTable(BaseTable):
    class Meta(BaseTable.Meta):
        model = Vehicle
        fields = ["brand", "license_plate", "year_of_production", "mileage", "vehicle_status"]


class VehicleStatusTable(BaseTable):
    class Meta(BaseTable.Meta):
        model = VehicleStatus
        fields = ["status"]


class TrailerTable(BaseTable):
    class Meta(BaseTable.Meta):
        model = Trailer
        fields = ["name", "width", "length", "height", "load_capacity"]

class VehicleTypeTable(BaseTable):
    class Meta(BaseTable.Meta):
        model = VehicleType
        fields = ["name"]


class UserActionLogTable(BaseTable):
    class Meta(BaseTable.Meta):
        model = UserActionLog
        fields = ["user", "model_name", "object_id", "action", "status", "created_at"]
