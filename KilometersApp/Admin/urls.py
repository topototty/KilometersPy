from django.urls import path
from KilometersApp.Admin import views

urlpatterns = [
    path('panel/', views.admin_panel, name='admin_panel'),
    path('logs/', views.UserActionLogListView.as_view(), name='admin_log'),
    path('stats/', views.orders_stats_view, name='admin_stats'),

    path('backups/', views.BackupListView.as_view(), name='backup_list'),
    path('backups/restore/<str:filename>/', views.BackupRestoreView.as_view(), name='backup_restore'),
    path('backups/delete/<str:filename>/', views.BackupDeleteView.as_view(), name='backup_delete'),
    path('backups/create/', views.BackupCreateView.as_view(), name='backup_create'),

    # User
    path("users/create/", views.UserCreateView.as_view(), name="userproxy_create"),
    path("users/<int:pk>/update/", views.UserUpdateView.as_view(), name="userproxy_update"),
    path("users/<int:pk>/delete/", views.UserDeleteView.as_view(), name="userproxy_delete"),

    # Order
    path('orders/create/', views.OrderCreateView.as_view(), name='order_create'),
    path('orders/<int:pk>/update/', views.OrderUpdateView.as_view(), name='order_update'),
    path('orders/<int:pk>/delete/', views.OrderDeleteView.as_view(), name='order_delete'),

    # CargoType
    path('cargo-types/create/', views.CargoTypeCreateView.as_view(), name='cargotype_create'),
    path('cargo-types/<int:pk>/update/', views.CargoTypeUpdateView.as_view(), name='cargotype_update'),
    path('cargo-types/<int:pk>/delete/', views.CargoTypeDeleteView.as_view(), name='cargotype_delete'),

    # OrderStatus
    path('order-statuses/create/', views.OrderStatusCreateView.as_view(), name='orderstatus_create'),
    path('order-statuses/<int:pk>/update/', views.OrderStatusUpdateView.as_view(), name='orderstatus_update'),
    path('order-statuses/<int:pk>/delete/', views.OrderStatusDeleteView.as_view(), name='orderstatus_delete'),

    # Route
    path('routes/create/', views.RouteCreateView.as_view(), name='route_create'),
    path('routes/<int:pk>/update/', views.RouteUpdateView.as_view(), name='route_update'),
    path('routes/<int:pk>/delete/', views.RouteDeleteView.as_view(), name='route_delete'),

    # Driver
    path('drivers/create/', views.DriverCreateView.as_view(), name='driver_create'),
    path('drivers/<int:pk>/update/', views.DriverUpdateView.as_view(), name='driver_update'),
    path('drivers/<int:pk>/delete/', views.DriverDeleteView.as_view(), name='driver_delete'),


    # Vehicle
    path('vehicles/create/', views.VehicleCreateView.as_view(), name='vehicle_create'),
    path('vehicles/<int:pk>/update/', views.VehicleUpdateView.as_view(), name='vehicle_update'),
    path('vehicles/<int:pk>/delete/', views.VehicleDeleteView.as_view(), name='vehicle_delete'),

    # VehicleStatus
    path('vehicle-statuses/create/', views.VehicleStatusCreateView.as_view(), name='vehiclestatus_create'),
    path('vehicle-statuses/<int:pk>/update/', views.VehicleStatusUpdateView.as_view(), name='vehiclestatus_update'),
    path('vehicle-statuses/<int:pk>/delete/', views.VehicleStatusDeleteView.as_view(), name='vehiclestatus_delete'),

    # Trailer
    path('trailers/create/', views.TrailerCreateView.as_view(), name='trailer_create'),
    path('trailers/<int:pk>/update/', views.TrailerUpdateView.as_view(), name='trailer_update'),
    path('trailers/<int:pk>/delete/', views.TrailerDeleteView.as_view(), name='trailer_delete'),

    # VehicleType
    path('vehicle-types/create/', views.VehicleTypeCreateView.as_view(), name='vehicletype_create'),
    path('vehicle-types/<int:pk>/update/', views.VehicleTypeUpdateView.as_view(), name='vehicletype_update'),
    path('vehicle-types/<int:pk>/delete/', views.VehicleTypeDeleteView.as_view(), name='vehicletype_delete'),
]
