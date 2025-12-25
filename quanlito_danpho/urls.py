"""
URL configuration for quanlito_danpho project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ==================================================
    # 1. TRANG QUẢN TRỊ (ADMIN SITE)
    # ==================================================
    path('admin/', admin.site.urls),

    # ==================================================
    # 2. API ENDPOINTS (Cốt lõi)
    # ==================================================
    # Trỏ tất cả các đường dẫn bắt đầu bằng 'api/' vào app Core.
    # Ví dụ:
    #   - http://127.0.0.1:8000/api/ho-gia-dinh/
    #   - http://127.0.0.1:8000/api/auth/login/
    path('api/', include('apps.core.urls')),

    # ==================================================
    # 3. HỖ TRỢ REST FRAMEWORK
    # ==================================================
    # Thêm đường dẫn này để hiện nút "Log in" ở góc phải giao diện Browsable API
    path('api-auth/', include('rest_framework.urls')),
]

# ==================================================
# 4. CẤU HÌNH MEDIA (HIỂN THỊ ẢNH)
# ==================================================
# Chỉ chạy khi DEBUG = True (Môi trường Dev)
# Giúp xem được ảnh minh chứng/avatar trực tiếp trên trình duyệt
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)