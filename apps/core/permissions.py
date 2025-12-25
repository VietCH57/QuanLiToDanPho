from rest_framework.permissions import BasePermission

# ==========================================================
#  NHÓM QUYỀN CƠ BẢN (DÂN CƯ & CÁN BỘ)
# ==========================================================

class IsNguoiDan(BasePermission):
    """
    Quyền truy cập: Chỉ dành cho công dân (NGUOI_DAN).
    - Thường dùng cho các API xem thông tin cá nhân hoặc gửi đơn kiến nghị.
    """
    def has_permission(self, request, view):
        # 1. Phải đăng nhập
        if not (request.user and request.user.is_authenticated):
            return False
            
        # 2. Phải có Profile (Tránh lỗi nếu là Admin hệ thống đăng nhập)
        if not hasattr(request.user, 'profile'):
            return False
            
        # 3. Check vai trò
        return request.user.profile.role == 'NGUOI_DAN'


class IsCanBo(BasePermission):
    """
    Quyền truy cập: Dành cho Cán bộ chức năng và Lãnh đạo tổ.
    - Bao gồm: Cán bộ nhân khẩu, Cán bộ hành chính, Tổ trưởng, Tổ phó.
    - Thường dùng cho API xử lý nghiệp vụ, duyệt đơn, xem báo cáo.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        # Danh sách các vai trò được coi là "Cán bộ"
        ALLOWED_ROLES = [
            'CAN_BO_NHAN_KHAU',
            'CAN_BO_HANH_CHINH',
            'TO_TRUONG',
            'TO_PHO',
            'CAN_BO' # (Giữ lại để tương thích với dữ liệu cũ nếu có)
        ]

        return (
            hasattr(request.user, 'profile') 
            and request.user.profile.role in ALLOWED_ROLES
        )


# ==========================================================
#  NHÓM QUYỀN QUẢN TRỊ & LÃNH ĐẠO
# ==========================================================

class IsToTruong(BasePermission):
    """
    Quyền truy cập cấp cao: Chỉ dành riêng cho TỔ TRƯỞNG.
    - Có quyền cao nhất trong các nghiệp vụ dân phố.
    """
    def has_permission(self, request, view):
        return (
            request.user 
            and request.user.is_authenticated 
            and hasattr(request.user, 'profile') 
            and request.user.profile.role == 'TO_TRUONG'
        )


class IsAdminOrToTruong(BasePermission):
    """
    Quyền Quản trị User (Đặc biệt):
    - Cho phép: Admin hệ thống (Superuser) HOẶC Tổ trưởng.
    - Mục đích: Dùng cho API tạo tài khoản cấp dưới (User Management).
    """
    def has_permission(self, request, view):
        # Trường hợp 1: Là Admin hệ thống (Superuser của Django) -> Luôn được phép
        if request.user and request.user.is_superuser:
            return True
            
        # Trường hợp 2: Là Tổ trưởng
        is_to_truong = (
            request.user 
            and request.user.is_authenticated 
            and hasattr(request.user, 'profile') 
            and request.user.profile.role == 'TO_TRUONG'
        )
        return is_to_truong