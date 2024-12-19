from django import forms
from django.core.validators import validate_email, RegexValidator, MinValueValidator, MaxValueValidator
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from KilometersApp.models import *
from django.contrib.auth import password_validation

class BaseModelForm(forms.ModelForm):
    """
    Базовая форма для наследования, добавляет стили, placeholder и help_text.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget = field.widget

            # Добавляем классы для различных типов виджетов
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.update({"class": "form-check-input"})
            elif isinstance(widget, forms.RadioSelect):
                widget.attrs.update({"class": "form-check-input"})
            elif isinstance(widget, forms.Select):
                widget.attrs.update({"class": "form-select"})
            elif isinstance(widget, (forms.Textarea, forms.TextInput, forms.EmailInput, forms.URLInput, forms.NumberInput, forms.PasswordInput)):
                widget.attrs.update({"class": "form-control"})
            elif isinstance(widget, forms.ClearableFileInput):
                widget.attrs.update({"class": "form-control-file"})
            elif isinstance(widget, forms.DateInput):
                widget.attrs.update({"class": "form-control datepicker"})
            elif isinstance(widget, forms.DateTimeInput):
                widget.attrs.update({"class": "form-control datetimepicker"})
            elif isinstance(widget, forms.TimeInput):
                widget.attrs.update({"class": "form-control timepicker"})
            else:
                widget.attrs.update({"class": "form-control"})

            # Placeholder
            if hasattr(self.Meta, 'placeholders') and field_name in self.Meta.placeholders:
                widget.attrs.update({"placeholder": self.Meta.placeholders[field_name]})

            # Help text
            if hasattr(self.Meta, 'help_texts') and field_name in self.Meta.help_texts:
                field.help_text = self.Meta.help_texts[field_name]


class UserForm(BaseModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Введите пароль", "class": "form-control"}),
        label="Пароль",
        help_text="Пароль для нового пользователя.",
        min_length=8,
        required=False,  # Пароль необязателен при редактировании
        validators=[
            RegexValidator(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@#$%^&+=]{8,}$', 
                           "Пароль должен содержать буквы, цифры и быть длиной не менее 8 символов.")
        ]
    )
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "form-select"}),
        required=False,
        label="Группы",
        help_text="Выберите группы, к которым будет принадлежать пользователь.",
    )
    phone = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "+7-___-___--", "class": "form-control", "id":"phone" }),
        label="Телефон",
        help_text="Номер телефона пользователя.",
    )
    email = forms.EmailField(
        required=True,
        validators=[validate_email],
        widget=forms.EmailInput(attrs={"placeholder": "Введите email", "class": "form-control"}),
        label="Email"
    )

    class Meta:
        model = User
        fields = ["username", "email", "is_staff", "password", "groups", "phone"]

    def init(self, *args, **kwargs):
        super().init(*args, **kwargs)
        # Если форма связана с существующим пользователем, заполняем телефон
        if self.instance and self.instance.pk:
            try:
                profile = self.instance.profile
                self.fields["phone"].initial = profile.phone
                # Также отображаем существующий пароль в случае редактирования
            except Profile.DoesNotExist:
                pass

    def clean_password(self):
        # Если пароль не был изменен, то ничего не делаем
        password = self.cleaned_data.get('password')
        if not password:
            return self.instance.password  # Возвращаем существующий пароль пользователя
        else:
            # Если пароль был изменен, проверяем его на соответствие условиям
            password_validation.validate_password(password)
            return password

    def save(self, commit=True):
        user = super().save(commit=False)
        if 'password' in self.changed_data and self.cleaned_data.get('password'):
            user.set_password(self.cleaned_data['password'])  # Устанавливаем новый пароль
        if commit:
            user.save()
        return user


class ProfileForm(BaseModelForm):
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Введите номер телефона", "class": "form-control", "id":"phone" }),
        label="Телефон",
    )

    class Meta:
        model = Profile
        fields = ["user", "is_deleted"]
        help_texts = {
            "user": "Пользователь, связанный с этим профилем.",
            "is_deleted": "Отметьте, если профиль удален.",
        }


class OrderForm(BaseModelForm):
    cargo_weight = forms.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01), MaxValueValidator(9999.99)],
        label="Вес груза",
        help_text="Введите вес груза в пределах от 0.01 до 9999.99."
    )

    class Meta:
        model = Order
        fields = [
            "order_number", "cargo_width", "cargo_length", "cargo_weight", 
            "cargo_description", "origin_address", "destination_address", 
            "delivery_date", "delivery_time", "user_id", "cargo_type", 
            "vehicle_type", "order_status"
        ]


class CargoTypeForm(BaseModelForm):
    name = forms.CharField(
        validators=[RegexValidator(r'^[a-zA-Zа-яА-Я\s]+$', "Название должно содержать только буквы.")],
        label="Название типа груза"
    )

    class Meta:
        model = CargoType
        fields = ["name"]


class OrderStatusForm(BaseModelForm):
    class Meta:
        model = OrderStatus
        fields = ["name"]


class RouteForm(BaseModelForm):
    class Meta:
        model = Route
        fields = ["route_number", "order_id", "driver_id", "vehicle_id"]


class DriverForm(BaseModelForm):
    drivers_license_number = forms.CharField(
        validators=[RegexValidator(r'^[A-Z0-9]{6,15}$', "Введите корректный номер водительского удостоверения.")],
        label="Номер водительского удостоверения"
    )

    # Исключаем пользователей, которые уже назначены водителями, но добавляем текущего водителя
    user_id = forms.ModelChoiceField(
        queryset=User.objects.all(),  # Начинаем с полного списка пользователей
        widget=forms.Select(attrs={"class": "form-select"}),
        required=True,
        label="Пользователь",
        help_text="Выберите пользователя, который будет водителем."
    )

    class Meta:
        model = Driver
        fields = [
            "user_id", "drivers_license_number", 
            "date_of_issue_of_drivers_license", 
            "expiration_date_of_drivers_license", 
            "license_categories"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Исключаем текущего водителя из списка доступных пользователей
        if self.instance and self.instance.pk:
            # Отфильтровываем пользователей, исключая тех, кто уже является водителем, но добавляем текущего водителя
            self.fields['user_id'].queryset = User.objects.exclude(
                id__in=Driver.objects.exclude(driver_id=self.instance.driver_id).values('user_id')
            )
            # Устанавливаем пользователя по умолчанию
            self.fields['user_id'].initial = self.instance.user_id



class VehicleForm(BaseModelForm):
    license_plate = forms.CharField(
        label="Госномер",
        widget=forms.TextInput(attrs={
            "placeholder": "A000AA-00",
            "class": "form-control",
            "id": "license_plate"
        }),
        help_text="Введите госномер в формате A000AA-00."
    )

    class Meta:
        model = Vehicle
        fields = [
            "brand", "license_plate", "year_of_production", 
            "mileage", "vehicle_status", "trailer_id", "vehicle_type_id"
        ]


class VehicleStatusForm(BaseModelForm):
    class Meta:
        model = VehicleStatus
        fields = ["status"]


class TrailerForm(BaseModelForm):
    class Meta:
        model = Trailer
        fields = [
            "name", "width", "length", "height", 
            "load_capacity", "measurement_unit_id", "vehicle_type_id"
        ]


class VehicleTypeForm(BaseModelForm):
    class Meta:
        model = VehicleType
        fields = ["name"]
