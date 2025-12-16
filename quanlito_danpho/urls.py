# urls.py placeholder — add URL patterns after project init.

from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]