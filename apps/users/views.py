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
    Trang dashboard với nội dung khác nhau theo role
    """
    user_profile = request.user.profile
    role = user_profile.role
    
    # Nội dung theo role
    if role in ['admin', 'citizenship_manager', 'commendation_manager']:
        message = "hú, bạn là tinh hoa, oách vl"
        role_class = "manager"
    else:  # citizen
        message = "con gà máu bùn"
        role_class = "citizen"
    
    context = {
        'user_profile': user_profile,
        'role_display': user_profile.get_role_display(),
        'message': message,
        'role_class': role_class,
    }
    
    return render(request, 'users/dashboard.html', context)
