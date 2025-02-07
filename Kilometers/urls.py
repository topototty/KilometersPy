from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin-django/', admin.site.urls),
    path('', include('KilometersApp.routing')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)