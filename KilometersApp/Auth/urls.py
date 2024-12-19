from django.urls import path, include
from KilometersApp.Auth import views


urlpatterns = [
    path('login/', views.userLogin, name="login"),
    path('reg/', views.registration, name="reg"),
    path("logout/", views.user_logout, name="logout"),
]
