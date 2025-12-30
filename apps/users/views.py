from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

def register_view(request):
    """
    Xử lý đăng ký tài khoản mới
    Username = CCCD
    """
    # Nếu đã đăng nhập -> Chuyển hướng sang Dashboard
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    
    if request.method == 'POST':
        cccd = request.POST.get('cccd', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        full_name = request.POST.get('full_name', '').strip()
        
        # Validate dữ liệu
        if not cccd:
            messages.error(request, 'Vui lòng nhập số CCCD!')
            return render(request, 'users/register.html')
        
        if not password:
            messages.error(request, 'Vui lòng nhập mật khẩu!')
            return render(request, 'users/register.html')
        
        if len(password) < 6:
            messages.error(request, 'Mật khẩu phải có ít nhất 6 ký tự!')
            return render(request, 'users/register.html')
        
        if password != password_confirm:
            messages.error(request, 'Mật khẩu xác nhận không khớp!')
            return render(request, 'users/register.html')
        
        # Kiểm tra CCCD đã tồn tại chưa (kiểm tra cả username và cccd_id trong profile)
        if User.objects.filter(username=cccd).exists():
            messages.error(request, 'Số CCCD này đã được đăng ký!')
            return render(request, 'users/register.html')
        
        try:
            # Tạo user mới với username = CCCD
            user = User.objects.create_user(
                username=cccd,
                password=password
            )
            
            # Cập nhật profile (đã được tạo tự động bởi signal)
            user.profile.cccd_id = cccd
            user.profile.full_name = full_name
            user.profile.role = 'citizen'  # Mặc định là dân cư
            user.profile.save()
            
            messages.success(request, 'Đăng ký thành công! Bạn có thể đăng nhập ngay.')
            return redirect('users:login')
            
        except Exception as e:
            messages.error(request, f'Có lỗi xảy ra: {str(e)}')
            return render(request, 'users/register.html')
    
    return render(request, 'users/register.html')

def login_view(request):
    """
    Xử lý đăng nhập người dùng
    """
    # 1. Nếu đã đăng nhập -> Chuyển hướng sang Dashboard
    if request.user.is_authenticated:
        # SỬA: Phải là 'users' (số nhiều) và có dấu hai chấm
        return redirect('users:dashboard') 
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Chào mừng {username}!')
                
                # 2. Đăng nhập thành công -> Chuyển hướng sang Dashboard
                # SỬA: Thêm 'users:' vào trước
                return redirect('users:dashboard')
            else:
                messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng')
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng')
    else:
        form = AuthenticationForm()
    
    return render(request, 'users/login.html', {'form': form})


@login_required
def logout_view(request):
    """
    Xử lý đăng xuất người dùng
    """
    logout(request)
    messages.success(request, 'Đã đăng xuất thành công!')
    return redirect('users:login')


@login_required
def dashboard_view(request):
    """
    Trang chủ với các nút điều hướng chính
    """
    user_profile = request.user.profile
    role = user_profile.role
    
    # Kiểm tra quyền admin
    is_admin = role == 'admin' or request.user.is_superuser
    
    context = {
        'user_profile': user_profile,
        'role_display': user_profile.get_role_display(),
        'is_admin': is_admin,
    }
    
    return render(request, 'users/dashboard.html', context)


@login_required
def nhan_khau_view(request):
    """Trang khai báo và tra cứu nhân khẩu"""
    return render(request, 'users/nhan_khau.html')


@login_required
def ho_khau_view(request):
    """Trang quản lý hộ khẩu"""
    return render(request, 'users/ho_khau.html')


@login_required
def tam_tru_tam_vang_view(request):
    """Trang khai báo tạm trú - tạm vắng"""
    return render(request, 'users/tam_tru_tam_vang.html')


@login_required
def khen_thuong_view(request):
    """Trang khen thưởng"""
    return render(request, 'users/khen_thuong.html')


@login_required
def quan_ly_nguoi_dung_view(request):
    """Trang quản lý người dùng (chỉ admin)"""
    # Kiểm tra quyền admin
    if request.user.profile.role != 'admin' and not request.user.is_superuser:
        messages.error(request, 'Bạn không có quyền truy cập trang này!')
        return redirect('users:dashboard')
    
    return render(request, 'users/quan_ly_nguoi_dung.html')
