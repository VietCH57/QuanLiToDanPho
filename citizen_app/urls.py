from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

# --- 1. Import thư viện Swagger (Mới thêm) ---
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# --- 2. Cấu hình thông tin trang Tài liệu API ---
schema_view = get_schema_view(
   openapi.Info(
      title="Tài Liệu API Quản Lý Tổ Dân Phố",
      default_version='v1',
      description="Tài liệu chi tiết cho Frontend (Có thể test API trực tiếp tại đây)",
      contact=openapi.Contact(email="admin@todanpho.com"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 1. Đường dẫn cho Users (Login, Dashboard...)
    path('users/', include('apps.users.urls')),
    
    # 2. Đường dẫn cho Core (Quản lý dân cư, hộ khẩu...)
    path('core/', include('apps.core.urls')), 
    
    # 3. Đường dẫn API (Đã hoạt động)
    path('api/', include('apps.api.urls')),

    # 4. Đường dẫn Swagger (Mới thêm)
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # 5. Trang chủ mặc định -> Chuyển hướng về Login
    path('', lambda request: redirect('users:login')), 
]

# Cấu hình file tĩnh (Hỗ trợ hiển thị giao diện đẹp cho Admin & Swagger)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)