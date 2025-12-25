from django.urls import path, include
from rest_framework.routers import DefaultRouter

# 1. Import các Views NGHIỆP VỤ từ api_views.py
from .api_views import (
    HoGiaDinhViewSet, ThanhVienViewSet, 
    DanhMucPhanThuongViewSet, LichSuPhatThuongViewSet, 
    TamTruViewSet, TamVangViewSet, UserManagementViewSet,
    DashboardView
)

# 2. Import các Views XÁC THỰC từ views_auth.py (MỚI)
from .views_auth import (
    RegisterView, LoginView, LogoutView, 
    UserProfileView, ChangePasswordView
)

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
    # --- AUTHENTICATION (Sử dụng views từ views_auth.py) ---
    path('auth/register/', RegisterView.as_view(), name='auth_register'),       # Đăng ký (Mới)
    path('auth/login/', LoginView.as_view(), name='auth_login'),                # Đăng nhập
    path('auth/logout/', LogoutView.as_view(), name='auth_logout'),             # Đăng xuất
    path('auth/change-password/', ChangePasswordView.as_view(), name='auth_change_password'), # Đổi mật khẩu (Mới)
    
    # --- PROFILE ---
    path('me/', UserProfileView.as_view(), name='my_profile'),                  # Xem thông tin bản thân

    # --- DASHBOARD ---
    path('dashboard/', DashboardView.as_view(), name='dashboard'),              # Báo cáo tổng quan

    # --- Include toàn bộ API từ Router ---
    path('', include(router.urls)),
]