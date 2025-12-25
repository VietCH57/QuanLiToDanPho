from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from apps.core.models import HoGiaDinh, ThanhVien, TamTru, TamVang, DanhMucPhanThuong, LichSuPhatThuong

# Import decorators phân quyền
from .decorators import (
    role_required, admin_required, manager_required,
    citizenship_manager_required, commendation_manager_required,
    is_manager, is_citizenship_manager, is_commendation_manager
)


def login_view(request):
    """
    Xử lý đăng nhập người dùng
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Chào mừng {username}!')
                return redirect('dashboard')
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
    return redirect('login')


@login_required
def dashboard_view(request):
    """
    Trang dashboard với nội dung khác nhau theo role
    """
    user_profile = request.user.profile
    role = user_profile.role
    
    # Thống kê chung
    stats = {
        'total_hokhau': HoGiaDinh.objects.count(),
        'total_nhankhau': ThanhVien.objects.count(),
        'total_tamtru': TamTru.objects.filter(trang_thai='ChoDuyet').count() if hasattr(TamTru, 'trang_thai') else TamTru.objects.count(),
        'total_khenthuong': LichSuPhatThuong.objects.count(),
    }
    
    # Xác định quyền hạn để hiển thị trong template
    permissions = {
        'can_manage_citizens': role in ['admin', 'citizenship_manager'],
        'can_manage_commendations': role in ['admin', 'commendation_manager'],
        'is_admin': role == 'admin',
        'is_manager': role in ['admin', 'citizenship_manager', 'commendation_manager'],
    }
    
    # Nội dung theo role
    if role == 'admin':
        message = "Quản trị viên - Toàn quyền quản lý hệ thống"
        role_class = "admin"
    elif role == 'citizenship_manager':
        message = "Quản lý công dân - Quản lý hộ khẩu, nhân khẩu, tạm trú"
        role_class = "manager"
    elif role == 'commendation_manager':
        message = "Quản lý khen thưởng - Quản lý phần thưởng và phát thưởng"
        role_class = "manager"
    else:  # citizen
        message = "Người dân - Xem thông tin cá nhân"
        role_class = "citizen"
    
    context = {
        'user_profile': user_profile,
        'role_display': user_profile.get_role_display(),
        'message': message,
        'role_class': role_class,
        'stats': stats,
        'permissions': permissions,
    }
    
    return render(request, 'users/dashboard.html', context)


# ===== PROFILE & CHANGE PASSWORD =====
@login_required
def profile_view(request):
    """Xem thông tin cá nhân"""
    return render(request, 'accounts/profile.html')


@login_required
def change_password_view(request):
    """Đổi mật khẩu"""
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not request.user.check_password(old_password):
            messages.error(request, 'Mật khẩu cũ không đúng')
        elif new_password != confirm_password:
            messages.error(request, 'Mật khẩu mới không khớp')
        elif len(new_password) < 6:
            messages.error(request, 'Mật khẩu mới phải có ít nhất 6 ký tự')
        else:
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Đổi mật khẩu thành công!')
            return redirect('dashboard')
    
    return render(request, 'accounts/change_password.html')


# ===== HỘ KHẨU VIEWS =====
@login_required
def hokhau_list_view(request):
    """Danh sách hộ khẩu - Tất cả đều được xem"""
    hokhau_list = HoGiaDinh.objects.all().order_by('ma_ho')
    can_edit = is_citizenship_manager(request.user)
    return render(request, 'hokhau/list.html', {
        'hokhau_list': hokhau_list,
        'can_edit': can_edit
    })


@login_required
def hokhau_detail_view(request, pk):
    """Chi tiết hộ khẩu - Tất cả đều được xem"""
    hokhau = get_object_or_404(HoGiaDinh, pk=pk)
    thanh_vien_list = hokhau.thanh_vien_trong_ho.all()
    can_edit = is_citizenship_manager(request.user)
    return render(request, 'hokhau/detail.html', {
        'hokhau': hokhau,
        'thanh_vien_list': thanh_vien_list,
        'can_edit': can_edit
    })


@login_required
@citizenship_manager_required
def hokhau_form_view(request, pk=None):
    """Thêm/Sửa hộ khẩu - Chỉ Quản lý công dân"""
    hokhau = get_object_or_404(HoGiaDinh, pk=pk) if pk else None
    
    if request.method == 'POST':
        ma_ho = request.POST.get('ma_ho')
        dia_chi = request.POST.get('dia_chi')
        
        if hokhau:
            hokhau.ma_ho = ma_ho
            hokhau.dia_chi = dia_chi
            hokhau.save()
            messages.success(request, 'Cập nhật hộ khẩu thành công!')
        else:
            HoGiaDinh.objects.create(ma_ho=ma_ho, dia_chi=dia_chi)
            messages.success(request, 'Thêm hộ khẩu thành công!')
        return redirect('hokhau_list')
    
    return render(request, 'hokhau/form.html', {'hokhau': hokhau})


# ===== NHÂN KHẨU VIEWS =====
@login_required
def nhankhau_list_view(request):
    """Danh sách nhân khẩu - Tất cả đều được xem"""
    nhankhau_list = ThanhVien.objects.select_related('ho_gia_dinh').all().order_by('ho_ten')
    can_edit = is_citizenship_manager(request.user)
    return render(request, 'nhankhau/list.html', {
        'nhankhau_list': nhankhau_list,
        'can_edit': can_edit
    })


@login_required
def nhankhau_detail_view(request, pk):
    """Chi tiết nhân khẩu - Tất cả đều được xem"""
    nhankhau = get_object_or_404(ThanhVien, pk=pk)
    can_edit = is_citizenship_manager(request.user)
    return render(request, 'nhankhau/detail.html', {
        'nhankhau': nhankhau,
        'can_edit': can_edit
    })


@login_required
@citizenship_manager_required
def nhankhau_form_view(request, pk=None):
    """Thêm/Sửa nhân khẩu - Chỉ Quản lý công dân"""
    nhankhau = get_object_or_404(ThanhVien, pk=pk) if pk else None
    hokhau_list = HoGiaDinh.objects.all()
    
    if request.method == 'POST':
        ho_ten = request.POST.get('ho_ten')
        cccd = request.POST.get('cccd')
        ngay_sinh = request.POST.get('ngay_sinh')
        gioi_tinh = request.POST.get('gioi_tinh')
        ho_gia_dinh_id = request.POST.get('ho_gia_dinh')
        quan_he_chu_ho = request.POST.get('quan_he_chu_ho', '')
        
        try:
            ho_gia_dinh = HoGiaDinh.objects.get(pk=ho_gia_dinh_id)
            
            if nhankhau:
                nhankhau.ho_ten = ho_ten
                nhankhau.cccd = cccd
                nhankhau.ngay_sinh = ngay_sinh
                nhankhau.gioi_tinh = gioi_tinh
                nhankhau.ho_gia_dinh = ho_gia_dinh
                nhankhau.quan_he_chu_ho = quan_he_chu_ho
                nhankhau.save()
                messages.success(request, 'Cập nhật nhân khẩu thành công!')
            else:
                ThanhVien.objects.create(
                    ho_ten=ho_ten,
                    cccd=cccd,
                    ngay_sinh=ngay_sinh,
                    gioi_tinh=gioi_tinh,
                    ho_gia_dinh=ho_gia_dinh,
                    quan_he_chu_ho=quan_he_chu_ho
                )
                messages.success(request, 'Thêm nhân khẩu thành công!')
            return redirect('nhankhau_list')
        except HoGiaDinh.DoesNotExist:
            messages.error(request, 'Hộ gia đình không tồn tại')
    
    return render(request, 'nhankhau/form.html', {
        'nhankhau': nhankhau,
        'hokhau_list': hokhau_list
    })


# ===== TẠM TRÚ - TẠM VẮNG VIEWS =====
@login_required
def tamtru_list_view(request):
    """Danh sách tạm trú - tạm vắng - Tất cả đều được xem"""
    tamtru_list = TamTru.objects.select_related('thanh_vien').all().order_by('-ngay_bat_dau')
    tamvang_list = TamVang.objects.select_related('thanh_vien').all().order_by('-ngay_bat_dau')
    can_edit = is_citizenship_manager(request.user)
    return render(request, 'tamtru/list.html', {
        'tamtru_list': tamtru_list,
        'tamvang_list': tamvang_list,
        'can_edit': can_edit
    })


@login_required
@citizenship_manager_required
def tamtru_form_view(request, pk=None):
    """Thêm đăng ký tạm trú/tạm vắng - Chỉ Quản lý công dân"""
    nhankhau_list = ThanhVien.objects.all()
    
    if request.method == 'POST':
        thanh_vien_id = request.POST.get('thanh_vien')
        loai = request.POST.get('loai')
        ngay_bat_dau = request.POST.get('ngay_bat_dau')
        ngay_ket_thuc = request.POST.get('ngay_ket_thuc')
        ly_do = request.POST.get('ly_do', '')
        
        try:
            thanh_vien = ThanhVien.objects.get(pk=thanh_vien_id)
            
            if loai == 'tam_tru':
                dia_chi_goc = request.POST.get('dia_chi_goc', '')
                dia_chi_tam_tru = request.POST.get('dia_chi_tam_tru', '')
                TamTru.objects.create(
                    thanh_vien=thanh_vien,
                    dia_chi_thuong_tru_goc=dia_chi_goc,
                    dia_chi_tam_tru=dia_chi_tam_tru,
                    ly_do=ly_do,
                    ngay_bat_dau=ngay_bat_dau,
                    ngay_ket_thuc=ngay_ket_thuc if ngay_ket_thuc else None
                )
                messages.success(request, 'Đăng ký tạm trú thành công!')
            else:
                noi_den = request.POST.get('noi_den', '')
                TamVang.objects.create(
                    thanh_vien=thanh_vien,
                    noi_den=noi_den,
                    ly_do=ly_do,
                    ngay_bat_dau=ngay_bat_dau,
                    ngay_ket_thuc=ngay_ket_thuc if ngay_ket_thuc else None
                )
                messages.success(request, 'Đăng ký tạm vắng thành công!')
            return redirect('tamtru_list')
        except ThanhVien.DoesNotExist:
            messages.error(request, 'Nhân khẩu không tồn tại')
    
    return render(request, 'tamtru/form.html', {'nhankhau_list': nhankhau_list})


# ===== KHEN THƯỞNG VIEWS =====
@login_required
def khenthuong_list_view(request):
    """Danh sách khen thưởng - Tất cả đều được xem"""
    lichsu_list = LichSuPhatThuong.objects.select_related('thanh_vien', 'phan_thuong').all().order_by('-ngay_cap_phat')
    phanthuong_list = DanhMucPhanThuong.objects.all()
    can_edit = is_commendation_manager(request.user)
    return render(request, 'khenthuong/list.html', {
        'lichsu_list': lichsu_list,
        'phanthuong_list': phanthuong_list,
        'can_edit': can_edit
    })


@login_required
@commendation_manager_required
def khenthuong_form_view(request, pk=None):
    """Thêm phát thưởng - Chỉ Quản lý khen thưởng"""
    nhankhau_list = ThanhVien.objects.all()
    phanthuong_list = DanhMucPhanThuong.objects.all()
    
    if request.method == 'POST':
        thanh_vien_id = request.POST.get('thanh_vien')
        phan_thuong_id = request.POST.get('phan_thuong')
        dot_phat = request.POST.get('dot_phat')
        ghi_chu = request.POST.get('ghi_chu', '')
        
        try:
            thanh_vien = ThanhVien.objects.get(pk=thanh_vien_id)
            phan_thuong = DanhMucPhanThuong.objects.get(pk=phan_thuong_id)
            
            LichSuPhatThuong.objects.create(
                thanh_vien=thanh_vien,
                phan_thuong=phan_thuong,
                dot_phat=dot_phat,
                ghi_chu=ghi_chu,
                nguoi_cap=request.user
            )
            messages.success(request, 'Thêm phát thưởng thành công!')
            return redirect('khenthuong_list')
        except (ThanhVien.DoesNotExist, DanhMucPhanThuong.DoesNotExist):
            messages.error(request, 'Dữ liệu không hợp lệ')
    
    return render(request, 'khenthuong/form.html', {
        'nhankhau_list': nhankhau_list,
        'phanthuong_list': phanthuong_list
    })


# ===== QUẢN LÝ NGƯỜI DÙNG (CHỈ ADMIN) =====
from django.contrib.auth.models import User
from apps.users.models import UserProfile


@login_required
@admin_required
def user_list_view(request):
    """Danh sách người dùng - Chỉ Admin"""
    users = User.objects.select_related('profile').all().order_by('-date_joined')
    return render(request, 'users/user_list.html', {'users': users})


@login_required
@admin_required
def user_form_view(request, pk=None):
    """Thêm/Sửa người dùng - Chỉ Admin"""
    edit_user = get_object_or_404(User, pk=pk) if pk else None
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email', '')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        role = request.POST.get('role', 'citizen')
        password = request.POST.get('password', '')
        is_active = request.POST.get('is_active') == 'on'
        
        try:
            if edit_user:
                # Cập nhật user
                edit_user.email = email
                edit_user.first_name = first_name
                edit_user.last_name = last_name
                edit_user.is_active = is_active
                if password:
                    edit_user.set_password(password)
                edit_user.save()
                
                # Cập nhật profile
                if hasattr(edit_user, 'profile'):
                    edit_user.profile.role = role
                    edit_user.profile.full_name = f"{first_name} {last_name}".strip()
                    edit_user.profile.save()
                
                messages.success(request, f'Cập nhật người dùng "{edit_user.username}" thành công!')
            else:
                # Kiểm tra username đã tồn tại
                if User.objects.filter(username=username).exists():
                    messages.error(request, f'Tên đăng nhập "{username}" đã tồn tại!')
                    return render(request, 'users/user_form.html', {'edit_user': edit_user})
                
                # Tạo user mới
                new_user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password if password else 'password123',
                    first_name=first_name,
                    last_name=last_name,
                    is_active=is_active
                )
                
                # Profile sẽ được tạo tự động qua signal, cập nhật role
                if hasattr(new_user, 'profile'):
                    new_user.profile.role = role
                    new_user.profile.full_name = f"{first_name} {last_name}".strip()
                    new_user.profile.save()
                
                messages.success(request, f'Tạo người dùng "{username}" thành công!')
            
            return redirect('user_list')
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
    
    return render(request, 'users/user_form.html', {'edit_user': edit_user})


@login_required
@admin_required
def user_delete_view(request, pk):
    """Xóa người dùng - Chỉ Admin"""
    user_to_delete = get_object_or_404(User, pk=pk)
    
    # Không cho xóa chính mình
    if user_to_delete == request.user:
        messages.error(request, 'Không thể xóa tài khoản của chính mình!')
        return redirect('user_list')
    
    # Không cho xóa superuser
    if user_to_delete.is_superuser:
        messages.error(request, 'Không thể xóa tài khoản Superuser!')
        return redirect('user_list')
    
    username = user_to_delete.username
    user_to_delete.delete()
    messages.success(request, f'Đã xóa người dùng "{username}"!')
    return redirect('user_list')
