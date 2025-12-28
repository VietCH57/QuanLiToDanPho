from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import các Views NGHIỆP VỤ từ apps/core/api_views.py
from apps.core.api_views import (
    HoGiaDinhViewSet, ThanhVienViewSet,
    DanhMucPhanThuongViewSet, LichSuPhatThuongViewSet,
    TamTruViewSet, TamVangViewSet, UserManagementViewSet,
    DashboardView
)

# Import các Views XÁC THỰC từ apps/core/views_auth.py
from apps.core.views_auth import (
    RegisterView, LoginView, LogoutView,
    UserProfileView, ChangePasswordView
)

app_name = 'api'

# Khởi tạo Router (Tự động sinh URL cho các CRUD API)
router = DefaultRouter()

# ==========================================================
#  NHÓM 1: QUẢN LÝ DÂN CƯ (Cốt lõi)
# ==========================================================
router.register(r'ho-gia-dinh', HoGiaDinhViewSet, basename='hogiadinh')
router.register(r'thanh-vien', ThanhVienViewSet, basename='thanhvien')

# ==========================================================
#  NHÓM 2: QUẢN LÝ KHEN THƯỞNG
# ==========================================================
router.register(r'danh-muc-phan-thuong', DanhMucPhanThuongViewSet, basename='phanthuong')
router.register(r'lich-su-phan-thuong', LichSuPhatThuongViewSet, basename='lichsu')

# ==========================================================
#  NHÓM 3: QUẢN LÝ CƯ TRÚ (Tạm trú / Tạm vắng)
# ==========================================================
router.register(r'tam-tru', TamTruViewSet, basename='tamtru')
router.register(r'tam-vang', TamVangViewSet, basename='tamvang')

# ==========================================================
#  NHÓM 4: QUẢN TRỊ HỆ THỐNG (User & Role)
# ==========================================================
router.register(r'quan-ly-user', UserManagementViewSet, basename='quanlyuser')

# ==========================================================
#  DANH SÁCH URL
# ==========================================================
urlpatterns = [
    # --- AUTHENTICATION ---
    path('auth/register/', RegisterView.as_view(), name='auth_register'),
    path('auth/login/', LoginView.as_view(), name='auth_login'),
    path('auth/logout/', LogoutView.as_view(), name='auth_logout'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='auth_change_password'),

    # --- PROFILE ---
    path('me/', UserProfileView.as_view(), name='my_profile'),

    # --- DASHBOARD ---
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    # --- Include toàn bộ API từ Router ---
    path('', include(router.urls)),
]