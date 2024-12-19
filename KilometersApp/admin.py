from django.contrib import admin
from .models import *

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone')
    search_fields = ('user__username', )
    list_filter = ('user__is_staff',)

    def get_encrypted_phone(self, obj):
        return obj.encrypted_phone
    get_encrypted_phone.short_description = 'Зашифрованный номер телефона'

admin.site.register(Profile, ProfileAdmin)

@admin.register(Check)
class CheckAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user_id', 'decimal', 'date', 'time')
    search_fields = ('order_id__order_number', 'user_id__username')
    list_filter = ('date', 'user_id')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'cargo_width', 'cargo_length', 'cargo_weight', 'origin_address', 'destination_address', 'delivery_date', 'delivery_time', 'user_id')
    search_fields = ('order_number', 'user_id__username')
    list_filter = ('delivery_date', 'cargo_type', 'order_status')

@admin.register(CargoType)
class CargoTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('route_number', 'order_id', 'driver_id', 'vehicle_id')
    search_fields = ('route_number',)
    list_filter = ('order_id', 'driver_id', 'vehicle_id')

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user_id', 'drivers_license_number', 'date_of_issue_of_drivers_license', 'expiration_date_of_drivers_license', 'driving_experience')
    search_fields = ('user_id__username', 'drivers_license_number')

    filter_horizontal = ('license_categories',)

    fieldsets = (
        (None, {
            'fields': ('user_id', 'drivers_license_number', 'date_of_issue_of_drivers_license', 'expiration_date_of_drivers_license', 'driving_experience', 'license_categories')
        }),
    )


@admin.register(DriversLicenseCategory)
class DriversLicenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('driver', 'category_name', 'category_description')

    def category_name(self, obj):
        return obj.category.name
    category_name.short_description = 'Название категории'
    def category_description(self, obj):
        return obj.category.description

    category_description.short_description = 'Описание категории'
    search_fields = ('category__name', 'category__description')

@admin.register(DriversLicenseCategoryType)
class DriversLicenseCategoryTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')
    list_filter = ('name',)

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('brand', 'license_plate', 'year_of_production', 'mileage', 'vehicle_status', 'trailer_id', 'vehicle_type_id')
    search_fields = ('license_plate',)
    list_filter = ('vehicle_status', 'vehicle_type_id')

@admin.register(VehicleStatus)
class VehicleStatusAdmin(admin.ModelAdmin):
    list_display = ('status',)
    search_fields = ('status',)

@admin.register(Trailer)
class TrailerAdmin(admin.ModelAdmin):
    list_display = ('name', 'width', 'length', 'height', 'load_capacity', 'measurement_unit_id', 'vehicle_type_id')
    search_fields = ('name',)
    list_filter = ('vehicle_type_id',)

@admin.register(MeasurementUnit)
class MeasurementUnitAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(VehicleType)
class VehicleTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(UserActionLog)
class UserActionLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'model_name', 'object_id', 'action', 'status', 'created_at')
    search_fields = ('user__username', 'model_name', 'action', 'status')
    list_filter = ('status', 'created_at', 'model_name')
    ordering = ('-created_at',)

    def has_add_permission(self, request):
        """Prevent adding logs manually from the admin interface."""
        return False

    def has_change_permission(self, request, obj=None):
        """Prevent editing logs from the admin interface."""
        return False
