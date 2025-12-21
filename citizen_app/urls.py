# urls.py placeholder — add URL patterns after project init.

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('apps.users.urls')),
    path('', lambda request: redirect('login')),  # Redirect root to login
]