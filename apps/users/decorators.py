# ==========================================================
#  DECORATORS PHÂN QUYỀN
#  Kiểm soát truy cập theo vai trò người dùng
# ==========================================================

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied


def role_required(*allowed_roles):
    """
    Decorator kiểm tra vai trò người dùng.
    
    Sử dụng:
        @role_required('admin', 'citizenship_manager')
        def my_view(request):
            ...
    
    Các vai trò:
        - admin: Quản trị viên (toàn quyền)
        - citizenship_manager: Quản lý công dân (nhân khẩu, hộ khẩu, tạm trú)
        - commendation_manager: Quản lý khen thưởng
        - citizen: Người dân (chỉ xem)
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Kiểm tra đăng nhập
            if not request.user.is_authenticated:
                messages.error(request, 'Vui lòng đăng nhập để tiếp tục.')
                return redirect('login')
            
            # Superuser luôn có quyền
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Kiểm tra profile
            if not hasattr(request.user, 'profile'):
                messages.error(request, 'Tài khoản chưa được cấu hình quyền.')
                return redirect('dashboard')
            
            user_role = request.user.profile.role
            
            # Kiểm tra vai trò
            if user_role in allowed_roles:
                return view_func(request, *args, **kwargs)
            
            # Không có quyền
            messages.error(request, 'Bạn không có quyền truy cập chức năng này.')
            return redirect('dashboard')
        
        return wrapper
    return decorator


def admin_required(view_func):
    """Chỉ cho phép Admin truy cập"""
    return role_required('admin')(view_func)


def manager_required(view_func):
    """Cho phép Admin hoặc bất kỳ Manager nào truy cập"""
    return role_required('admin', 'citizenship_manager', 'commendation_manager')(view_func)


def citizenship_manager_required(view_func):
    """Cho phép Admin hoặc Quản lý công dân truy cập"""
    return role_required('admin', 'citizenship_manager')(view_func)


def commendation_manager_required(view_func):
    """Cho phép Admin hoặc Quản lý khen thưởng truy cập"""
    return role_required('admin', 'commendation_manager')(view_func)


def can_view_only(view_func):
    """
    Decorator cho phép tất cả người dùng đăng nhập XEM,
    nhưng chặn các thao tác thay đổi (POST, PUT, DELETE)
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Vui lòng đăng nhập để tiếp tục.')
            return redirect('login')
        
        # Nếu là POST và không phải manager -> từ chối
        if request.method == 'POST':
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            if hasattr(request.user, 'profile'):
                if request.user.profile.role in ['admin', 'citizenship_manager', 'commendation_manager']:
                    return view_func(request, *args, **kwargs)
            
            messages.error(request, 'Bạn không có quyền thực hiện thao tác này.')
            return redirect(request.path)
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


# ==========================================================
#  HÀM TIỆN ÍCH KIỂM TRA QUYỀN
# ==========================================================

def has_permission(user, *allowed_roles):
    """
    Kiểm tra người dùng có quyền hay không.
    
    Sử dụng trong template hoặc view:
        if has_permission(request.user, 'admin', 'citizenship_manager'):
            # Cho phép thao tác
    """
    if not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    if not hasattr(user, 'profile'):
        return False
    
    return user.profile.role in allowed_roles


def is_admin(user):
    """Kiểm tra có phải Admin không"""
    return has_permission(user, 'admin')


def is_manager(user):
    """Kiểm tra có phải Manager (bất kỳ loại nào) không"""
    return has_permission(user, 'admin', 'citizenship_manager', 'commendation_manager')


def is_citizenship_manager(user):
    """Kiểm tra có quyền quản lý công dân không"""
    return has_permission(user, 'admin', 'citizenship_manager')


def is_commendation_manager(user):
    """Kiểm tra có quyền quản lý khen thưởng không"""
    return has_permission(user, 'admin', 'commendation_manager')


def is_citizen(user):
    """Kiểm tra có phải người dân không"""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return False
    if not hasattr(user, 'profile'):
        return True
    return user.profile.role == 'citizen'
