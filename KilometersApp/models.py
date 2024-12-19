from cryptography.fernet import Fernet
from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from django.contrib.auth import user_logged_out, user_logged_in
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.timezone import now
from django.contrib.sessions.models import Session
from KilometersApp.middleware import get_current_user


class UrlMixin:
    """
    Миксин для добавления методов генерации URL-адресов редактирования и удаления.
    """
    def get_edit_url(self):
        """
        Генерирует URL для редактирования объекта.
        Ожидает, что имя маршрута будет формата '<model_name>_update'.
        """
        return reverse(f'{self._meta.model_name}_update', kwargs={'pk': self.pk})

    def get_delete_url(self):
        """
        Генерирует URL для удаления объекта.
        Ожидает, что имя маршрута будет формата '<model_name>_delete'.
        """
        return reverse(f'{self._meta.model_name}_delete', kwargs={'pk': self.pk})
    
    def get_list_url(self):
        """
        Генерирует URL для списка объектов, который включает якорь для текущей вкладки.
        """
        model_name = self._meta.model_name  # Преобразуем в формат URL
        return f"{reverse('admin_panel')}#{self._meta.model_name}"
    
    def get_create_url(self):
        """
        Генерирует URL для создания объекта
        Ожидает, что имя маршрута будет формата '<model_name>_create'.
        """
        return reverse(f'{self._meta.model_name}_create')
    


#прокси-модель для того чтобы дописать к User миксин UrlMixin
class UserProxy(User, UrlMixin):
    class Meta:
        proxy = True
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")

        
class Profile(models.Model, UrlMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_('Пользователь'))
    encrypted_phone = models.TextField(verbose_name=_('Зашифрованный номер телефона'), null=True, blank=True)
    is_deleted = models.BooleanField(default=False, verbose_name=_('Удален'))
    fernet = Fernet(settings.ENCRYPTION_KEY)

    @property
    def phone(self):
        if self.encrypted_phone:
            return self.fernet.decrypt(self.encrypted_phone.encode()).decode()
        return None

    @phone.setter
    def phone(self, value):
        if value:
            self.encrypted_phone = self.fernet.encrypt(value.encode()).decode()

    class Meta:
        verbose_name = _("Профиль")
        verbose_name_plural = _("Профили")

    def __str__(self):
        return f"Профиль {self.user.username}"



class Check(models.Model, UrlMixin):
    order = models.OneToOneField('Order', on_delete=models.CASCADE, related_name='check_details', null=False,
                                 verbose_name=_('Заказ'))
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=False, verbose_name=_('Пользователь'))
    decimal = models.DecimalField(max_digits=10, decimal_places=2, null=False, verbose_name=_('Сумма'))
    date = models.DateField(null=False, verbose_name=_('Дата'))
    time = models.TimeField(null=False, verbose_name=_('Время'))

    class Meta:
        verbose_name = _("Чек")
        verbose_name_plural = _("Чеки")

    def __str__(self):
        return f"Чек для заказа {self.order.order_number} на сумму {self.decimal}"


class Order(models.Model, UrlMixin):
    order_id = models.AutoField(primary_key=True, verbose_name=_('ID заказа'))
    order_number = models.CharField(max_length=9, unique=True, null=False, verbose_name=_('Номер заказа'))
    cargo_width = models.DecimalField(max_digits=5, decimal_places=2, null=False, verbose_name=_('Ширина груза'))
    cargo_length = models.DecimalField(max_digits=5, decimal_places=2, null=False, verbose_name=_('Длина груза'))
    cargo_weight = models.DecimalField(max_digits=5, decimal_places=2, null=False, verbose_name=_('Вес груза'))
    cargo_description = models.TextField(null=False, verbose_name=_('Описание груза'))
    origin_address = models.CharField(max_length=255, null=False, verbose_name=_('Адрес отправления'))
    destination_address = models.CharField(max_length=255, null=False, verbose_name=_('Адрес доставки'))
    origin_coordinates = models.CharField(max_length=50, null=True, verbose_name=_('Координаты отправления'))
    destination_coordinates = models.CharField(max_length=50, null=True, verbose_name=_('Координаты доставки'))
    delivery_date = models.DateField(null=False, verbose_name=_('Дата доставки'))
    delivery_time = models.TimeField(null=False, verbose_name=_('Время доставки'))
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=False, verbose_name=_('Пользователь'))
    cargo_type = models.ForeignKey('CargoType', on_delete=models.CASCADE, null=False, verbose_name=_('Тип груза'))
    vehicle_type = models.ForeignKey('VehicleType', on_delete=models.CASCADE, null=False,
                                     verbose_name=_('Тип транспортного средства'))
    order_status = models.ForeignKey('OrderStatus', on_delete=models.CASCADE, null=False,
                                     verbose_name=_('Статус заказа'))
    
    def __str__(self):
        return f"Заказ {self.order_number}: {self.origin_address} -> {self.destination_address}"

    class Meta:
        verbose_name = _("Заказ")
        verbose_name_plural = _("Заказы")

    def create_check(self):
        """
        Создаёт чек для данного заказа, если он ещё не создан.
        Предполагается, что сумма чека будет равна цене из vehicle_type (можно изменить логику).
        """
        if not hasattr(self, 'check_details'):
            from django.utils.timezone import now
            from .models import Check  # Убедитесь, что импорт корректный (или перенесите его наверх файла)

            decimal = self.vehicle_type.price
            current_time = now()

            Check.objects.create(
                order=self,
                user_id=self.user_id,
                decimal=decimal,
                date=current_time.date(),
                time=current_time.time()
            )



class CargoType(models.Model, UrlMixin):
    cargo_type_id = models.AutoField(primary_key=True, verbose_name=_('ID типа груза'))
    name = models.CharField(max_length=50, null=False, verbose_name=_('Название типа груза'))

    class Meta:
        verbose_name = _("Тип груза")
        verbose_name_plural = _("Типы грузов")
    
    def __str__(self):
        return self.name
    


class OrderStatus(models.Model, UrlMixin):
    order_status_id = models.AutoField(primary_key=True, verbose_name=_('ID статуса'))
    name = models.CharField(max_length=50, null=False, verbose_name=_('Название статуса'))

    class Meta:
        verbose_name = _("Статус заказа")
        verbose_name_plural = _("Статусы заказов")

    def __str__(self):
        return self.name


class Route(models.Model, UrlMixin):
    route_id = models.AutoField(primary_key=True, verbose_name=_('ID маршрута'))
    route_number = models.CharField(max_length=50, unique=True, null=False, verbose_name=_('Номер маршрута'))
    order_id = models.ForeignKey('Order', on_delete=models.CASCADE, null=False, verbose_name=_('Заказ'))
    driver_id = models.ForeignKey('Driver', on_delete=models.CASCADE, null=False, verbose_name=_('Водитель'))
    vehicle_id = models.ForeignKey('Vehicle', on_delete=models.CASCADE, null=False,
                                   verbose_name=_('Транспортное средство'))

    class Meta:
        verbose_name = _("Маршрут")
        verbose_name_plural = _("Маршруты")

    def __str__(self):
        return f"Маршрут {self.route_number}: {self.order_id.order_number}"


class Driver(models.Model, UrlMixin):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, null=False, verbose_name=_('Пользователь'))
    driver_id = models.AutoField(primary_key=True, verbose_name=_('ID водителя'))
    drivers_license_number = models.CharField(max_length=15, unique=True, null=False, verbose_name=_('Номер водительского удостоверения'))
    date_of_issue_of_drivers_license = models.DateField(null=False, verbose_name=_('Дата выдачи ВУ'))
    expiration_date_of_drivers_license = models.DateField(null=False, verbose_name=_('Срок действия ВУ'))

    driving_experience = models.IntegerField(null=False, verbose_name=_('Стаж вождения (лет)'))

    license_categories = models.ManyToManyField('DriversLicenseCategoryType', related_name='drivers', verbose_name=_('Категории ВУ'))

    class Meta:
        verbose_name = _("Водитель")
        verbose_name_plural = _("Водители")

    def save(self, *args, **kwargs):
        today = timezone.now().date()
        self.driving_experience = (today - self.date_of_issue_of_drivers_license).days // 365

        super(Driver, self).save(*args, **kwargs)

        if self.license_categories.exists():
            for category in self.license_categories.all():
                DriversLicenseCategory.objects.create(driver=self, category=category)

    def __str__(self):
        return f"Водитель {self.user_id.username}: {self.drivers_license_number} Стаж: {self.driving_experience}"


class DriversLicenseCategory(models.Model, UrlMixin):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='license_category_entries', verbose_name=_('Водитель'))
    category = models.ForeignKey('DriversLicenseCategoryType', on_delete=models.CASCADE, verbose_name=_('Категория ВУ'))

    class Meta:
        verbose_name = _("Категория ВУ водителя")
        verbose_name_plural = _("Категории ВУ водителей")
        unique_together = ('driver', 'category')

class DriversLicenseCategoryType(models.Model, UrlMixin):
    name = models.CharField(max_length=50, unique=True, verbose_name=_('Название категории ВУ'))
    description = models.TextField(verbose_name=_('Описание категории ВУ'))

    class Meta:
        verbose_name = _("Категория ВУ")
        verbose_name_plural = _("Категории ВУ")

    def __str__(self):
        return self.name


class Vehicle(models.Model, UrlMixin):
    vehicle_id = models.AutoField(primary_key=True, verbose_name=_('ID транспортного средства'))
    brand = models.CharField(max_length=50, null=False, verbose_name=_('Марка'))
    license_plate = models.CharField(max_length=20, null=False, verbose_name=_('Госномер'))
    year_of_production = models.IntegerField(null=False, verbose_name=_('Год выпуска'))
    mileage = models.IntegerField(null=False, verbose_name=_('Пробег'))
    vehicle_status = models.ForeignKey('VehicleStatus', on_delete=models.CASCADE, null=False, verbose_name=_('Статус'))
    trailer_id = models.ForeignKey('Trailer', on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('Прицеп'))
    vehicle_type_id = models.ForeignKey('VehicleType', on_delete=models.CASCADE, null=False, verbose_name=_('Тип ТС'))

    class Meta:
        verbose_name = _("Транспортное средство")
        verbose_name_plural = _("Транспортные средства")

    def __str__(self):
        return f"{self.brand} ({self.license_plate}) {self.vehicle_type_id.name}"


class VehicleStatus(models.Model, UrlMixin):
    vehicle_status_id = models.AutoField(primary_key=True, verbose_name=_('ID статуса'))
    status = models.CharField(max_length=50, null=False, verbose_name=_('Статус'))

    class Meta:
        verbose_name = _("Статус ТС")
        verbose_name_plural = _("Статусы ТС")

    def __str__(self):
        return f"{self.status}"


class Trailer(models.Model, UrlMixin):
    trailer_id = models.AutoField(primary_key=True, verbose_name=_('ID прицепа'))
    name = models.CharField(max_length=50, null=False, verbose_name=_('Название'))
    width = models.DecimalField(max_digits=5, decimal_places=2, null=False, verbose_name=_('Ширина'))
    length = models.DecimalField(max_digits=5, decimal_places=2, null=False, verbose_name=_('Длина'))
    height = models.DecimalField(max_digits=5, decimal_places=2, null=False, verbose_name=_('Высота'))
    load_capacity = models.DecimalField(max_digits=5, decimal_places=2, null=False, verbose_name=_('Грузоподъемность'))
    measurement_unit_id = models.ForeignKey('MeasurementUnit', on_delete=models.CASCADE, null=False,
                                            verbose_name=_('Единица измерения'))
    vehicle_type_id = models.ForeignKey('VehicleType', on_delete=models.CASCADE, null=False, verbose_name=_('Тип ТС'))

    class Meta:
        verbose_name = _("Прицеп")
        verbose_name_plural = _("Прицепы")


class MeasurementUnit(models.Model, UrlMixin):
    measurement_unit_id = models.AutoField(primary_key=True, verbose_name=_('ID единицы измерения'))
    name = models.CharField(max_length=50, null=False, verbose_name=_('Название'))

    class Meta:
        verbose_name = _("Единица измерения")
        verbose_name_plural = _("Единицы измерения")


class VehicleType(models.Model):
    vehicle_type_id = models.AutoField(primary_key=True, verbose_name=_('ID типа ТС'))
    name = models.CharField(max_length=50, null=False, verbose_name=_('Название'))
    max_length = models.DecimalField(max_digits=5, decimal_places=2, default=1, null=False, verbose_name=_('Максимальная длина (м)'))
    max_width = models.DecimalField(max_digits=5, decimal_places=2, default=1, null=False, verbose_name=_('Максимальная ширина (м)'))
    max_weight = models.DecimalField(max_digits=7, decimal_places=2, default=1, null=False, verbose_name=_('Максимальный вес (кг)'))
    price = models.DecimalField(max_digits=7, decimal_places=2, default=1, null=False, verbose_name=_('Минимальная цена'))
    image = models.ImageField(upload_to='vehicle_images/', null=True, default=1, blank=True, verbose_name=_('Изображение ТС'))

    class Meta:
        verbose_name = _("Тип ТС")
        verbose_name_plural = _("Типы ТС")

    def __str__(self):
        return self.name + " " + f"{self.max_length}м\nОт {self.price}₽"


class UserActionLog(models.Model, UrlMixin):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Пользователь")
    model_name = models.CharField(max_length=100, verbose_name="Название модели")
    object_id = models.CharField(max_length=255, verbose_name="ID объекта")
    action = models.CharField(max_length=255, verbose_name="Действие")
    status = models.CharField(
        max_length=20,
        choices=[('INFO', 'Информация'), ('ERROR', 'Ошибка')],
        default='INFO',
        verbose_name="Статус"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время")

    def __str__(self):
        return f"{self.user} - {self.action} - {self.created_at}"

    class Meta:
        verbose_name = "Лог действий"
        verbose_name_plural = "Логи действий"

@receiver(post_save)
def log_model_action(sender, instance, created, **kwargs):
    """Universal signal to log actions after saving a model (creation/update)."""
    if sender in [UserActionLog, Session]:
        return  # Do not log actions for the UserActionLog or Session models

    model_name = sender._meta.verbose_name  # Get the human-readable model name
    object_id = instance.pk
    action = "Created" if created else "Updated"
    status = 'INFO'

    # Check if the instance has a user attribute
    user = getattr(instance, 'user', None) or get_current_user()

    UserActionLog.objects.create(
        user=user,
        model_name=model_name,
        object_id=object_id,
        action=f"{action} {model_name} with ID {object_id}",
        status=status,
        created_at=now()
    )


# Сигнал для входа пользователя
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Сигнал для записи лога после успешного входа пользователя."""
    model_name = "User"
    object_id = user.pk
    action = "Вход"
    status = 'INFO'

    UserActionLog.objects.create(
        user=user,
        model_name=model_name,
        object_id=object_id,
        action=f"Пользователь {user.username} вошел в систему",
        status=status,
        created_at=now()
    )

# Сигнал для выхода пользователя
@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Сигнал для записи лога после выхода пользователя."""
    model_name = "User"
    object_id = user.pk
    action = "Выход"
    status = 'INFO'

    UserActionLog.objects.create(
        user=user,
        model_name=model_name,
        object_id=object_id,
        action=f"Пользователь {user.username} вышел из системы",
        status=status,
        created_at=now()
    )

@receiver(post_save, sender=UserActionLog)
def limit_log_entries(sender, instance, **kwargs):
    total_logs = UserActionLog.objects.count()

    if total_logs > 500:
        excess_logs = UserActionLog.objects.order_by('created_at')[:total_logs - 500]