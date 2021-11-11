from django.conf import settings
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path(f'admin{settings.ADMIN_SUFFIX}/', admin.site.urls),
    path('', include('nouns_triggers.urls'))
]
