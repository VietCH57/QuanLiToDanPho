from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

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
