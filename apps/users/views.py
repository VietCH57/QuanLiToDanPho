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
    user_profile = request.user.profile
    is_manager = user_profile.role in ['admin', 'citizenship_manager', 'commendation_manager']
    
    # Import models
    from apps.core.models import TamTru, TamVang
    
    if is_manager:
        # Cán bộ: Xem danh sách tất cả đơn
        don_tam_tru = TamTru.objects.all().order_by('-ngay_tao')
        don_tam_vang = TamVang.objects.all().order_by('-ngay_tao')
    else:
        # Người dân: Chỉ xem đơn của mình
        don_tam_tru = TamTru.objects.filter(cccd=user_profile.cccd_id).order_by('-ngay_tao')
        don_tam_vang = TamVang.objects.filter(cccd=user_profile.cccd_id).order_by('-ngay_tao')
    
    context = {
        'is_manager': is_manager,
        'don_tam_tru': don_tam_tru,
        'don_tam_vang': don_tam_vang,
    }
    
    return render(request, 'users/tam_tru_tam_vang.html', context)


@login_required
def khai_bao_tam_tru_view(request):
    """Form khai báo tạm trú"""
    from apps.core.models import TamTru, ThanhVien
    
    user_profile = request.user.profile
    
    # Lấy thông tin cá nhân từ ThanhVien nếu có
    thanh_vien = None
    try:
        thanh_vien = ThanhVien.objects.get(cccd=user_profile.cccd_id)
    except ThanhVien.DoesNotExist:
        pass
    
    if request.method == 'POST':
        # Lưu dữ liệu vào session để xem trước
        request.session['tam_tru_data'] = dict(request.POST)
        return redirect('users:xem_truoc_tam_tru')
    
    context = {
        'thanh_vien': thanh_vien,
        'user_profile': user_profile,
    }
    return render(request, 'users/khai_bao_tam_tru.html', context)


@login_required
def khai_bao_tam_vang_view(request):
    """Form khai báo tạm vắng"""
    from apps.core.models import TamVang, ThanhVien
    
    user_profile = request.user.profile
    
    # Lấy thông tin cá nhân từ ThanhVien nếu có
    thanh_vien = None
    try:
        thanh_vien = ThanhVien.objects.get(cccd=user_profile.cccd_id)
    except ThanhVien.DoesNotExist:
        pass
    
    if request.method == 'POST':
        # Lưu dữ liệu vào session để xem trước
        request.session['tam_vang_data'] = dict(request.POST)
        return redirect('users:xem_truoc_tam_vang')
    
    context = {
        'thanh_vien': thanh_vien,
        'user_profile': user_profile,
    }
    return render(request, 'users/khai_bao_tam_vang.html', context)


@login_required
def xem_truoc_tam_tru_view(request):
    """Xem trước thông tin đơn tạm trú trước khi gửi"""
    from apps.core.models import ThanhVien
    
    data = request.session.get('tam_tru_data', {})
    if not data:
        messages.error(request, 'Không tìm thấy dữ liệu đơn. Vui lòng điền lại form.')
        return redirect('users:khai_bao_tam_tru')
    
    # Convert list values to single values
    for key in data:
        if isinstance(data[key], list) and len(data[key]) > 0:
            data[key] = data[key][0]
    
    user_profile = request.user.profile
    thanh_vien = None
    try:
        thanh_vien = ThanhVien.objects.get(cccd=user_profile.cccd_id)
    except ThanhVien.DoesNotExist:
        pass
    
    context = {
        'data': data,
        'thanh_vien': thanh_vien,
        'user_profile': user_profile,
    }
    return render(request, 'users/xem_truoc_tam_tru.html', context)


@login_required
def xem_truoc_tam_vang_view(request):
    """Xem trước thông tin đơn tạm vắng trước khi gửi"""
    from apps.core.models import ThanhVien
    
    data = request.session.get('tam_vang_data', {})
    if not data:
        messages.error(request, 'Không tìm thấy dữ liệu đơn. Vui lòng điền lại form.')
        return redirect('users:khai_bao_tam_vang')
    
    # Convert list values to single values
    for key in data:
        if isinstance(data[key], list) and len(data[key]) > 0:
            data[key] = data[key][0]
    
    user_profile = request.user.profile
    thanh_vien = None
    try:
        thanh_vien = ThanhVien.objects.get(cccd=user_profile.cccd_id)
    except ThanhVien.DoesNotExist:
        pass
    
    context = {
        'data': data,
        'thanh_vien': thanh_vien,
        'user_profile': user_profile,
    }
    return render(request, 'users/xem_truoc_tam_vang.html', context)


@login_required
def gui_don_tam_tru_view(request):
    """Xác nhận và gửi đơn tạm trú"""
    from apps.core.models import TamTru, ThanhVien
    
    if request.method != 'POST':
        return redirect('users:khai_bao_tam_tru')
    
    data = request.session.get('tam_tru_data', {})
    if not data:
        messages.error(request, 'Không tìm thấy dữ liệu đơn.')
        return redirect('users:khai_bao_tam_tru')
    
    # Convert list values to single values
    for key in data:
        if isinstance(data[key], list) and len(data[key]) > 0:
            data[key] = data[key][0]
    
    user_profile = request.user.profile
    thanh_vien = None
    try:
        thanh_vien = ThanhVien.objects.get(cccd=user_profile.cccd_id)
    except ThanhVien.DoesNotExist:
        pass
    
    try:
        tam_tru = TamTru()
        
        # Thông tin người đăng ký
        tam_tru.thanh_vien = thanh_vien
        tam_tru.ho_ten = data.get('ho_ten', '')
        tam_tru.ngay_sinh = data.get('ngay_sinh') if data.get('ngay_sinh') else None
        tam_tru.gioi_tinh = data.get('gioi_tinh', '')
        tam_tru.cccd = data.get('cccd', '')
        tam_tru.so_dien_thoai = data.get('so_dien_thoai', '')
        tam_tru.dia_chi_thuong_tru = data.get('dia_chi_thuong_tru', '')
        
        # Thông tin chủ hộ
        tam_tru.chu_ho_ten = data.get('chu_ho_ten', '')
        tam_tru.chu_ho_cccd = data.get('chu_ho_cccd', '')
        
        # Thông tin chủ sở hữu
        tam_tru.chu_so_huu_ten = data.get('chu_so_huu_ten', '')
        tam_tru.chu_so_huu_cccd = data.get('chu_so_huu_cccd', '')
        tam_tru.chu_so_huu_nam_sinh = int(data.get('chu_so_huu_nam_sinh', 0)) if data.get('chu_so_huu_nam_sinh') else None
        
        # Thông tin tạm trú
        tam_tru.noi_tam_tru = data.get('noi_tam_tru', '')
        tam_tru.thoi_han_tam_tru = data.get('thoi_han_tam_tru', '')
        tam_tru.moi_quan_he = data.get('moi_quan_he', '')
        tam_tru.ngay_bat_dau = data.get('ngay_bat_dau') if data.get('ngay_bat_dau') else None
        tam_tru.ngay_ket_thuc = data.get('ngay_ket_thuc') if data.get('ngay_ket_thuc') else None
        
        tam_tru.save()
        
        # Xóa dữ liệu session
        del request.session['tam_tru_data']
        
        messages.success(request, 'Đã gửi đơn tạm trú thành công! Vui lòng chờ cán bộ phê duyệt.')
        return redirect('users:tam_tru_tam_vang')
    except Exception as e:
        messages.error(request, f'Có lỗi xảy ra: {str(e)}')
        return redirect('users:xem_truoc_tam_tru')


@login_required
def gui_don_tam_vang_view(request):
    """Xác nhận và gửi đơn tạm vắng"""
    from apps.core.models import TamVang, ThanhVien
    
    if request.method != 'POST':
        return redirect('users:khai_bao_tam_vang')
    
    data = request.session.get('tam_vang_data', {})
    if not data:
        messages.error(request, 'Không tìm thấy dữ liệu đơn.')
        return redirect('users:khai_bao_tam_vang')
    
    # Convert list values to single values
    for key in data:
        if isinstance(data[key], list) and len(data[key]) > 0:
            data[key] = data[key][0]
    
    user_profile = request.user.profile
    thanh_vien = None
    try:
        thanh_vien = ThanhVien.objects.get(cccd=user_profile.cccd_id)
    except ThanhVien.DoesNotExist:
        pass
    
    try:
        tam_vang = TamVang()
        
        # Thông tin người đăng ký
        tam_vang.thanh_vien = thanh_vien
        tam_vang.ho_ten = data.get('ho_ten', '')
        tam_vang.ngay_sinh = data.get('ngay_sinh') if data.get('ngay_sinh') else None
        tam_vang.gioi_tinh = data.get('gioi_tinh', '')
        tam_vang.cccd = data.get('cccd', '')
        tam_vang.so_dien_thoai = data.get('so_dien_thoai', '')
        tam_vang.dia_chi_thuong_tru = data.get('dia_chi_thuong_tru', '')
        
        # Thông tin tạm vắng
        tam_vang.noi_den = data.get('noi_den', '')
        tam_vang.ngay_bat_dau = data.get('ngay_bat_dau') if data.get('ngay_bat_dau') else None
        tam_vang.ngay_ket_thuc = data.get('ngay_ket_thuc') if data.get('ngay_ket_thuc') else None
        tam_vang.ly_do = data.get('ly_do', '')
        
        tam_vang.save()
        
        # Xóa dữ liệu session
        del request.session['tam_vang_data']
        
        messages.success(request, 'Đã gửi đơn tạm vắng thành công! Vui lòng chờ cán bộ phê duyệt.')
        return redirect('users:tam_tru_tam_vang')
    except Exception as e:
        messages.error(request, f'Có lỗi xảy ra: {str(e)}')
        return redirect('users:xem_truoc_tam_vang')


@login_required
def chi_tiet_tam_tru_view(request, pk):
    """Xem chi tiết đơn tạm trú (cho cán bộ phê duyệt và người dân xem đơn của mình)"""
    from apps.core.models import TamTru
    from django.utils import timezone
    
    user_profile = request.user.profile
    is_manager = user_profile.role in ['admin', 'citizenship_manager', 'commendation_manager']
    
    tam_tru = TamTru.objects.get(pk=pk)
    
    # Kiểm tra quyền: cán bộ xem tất cả, người dân chỉ xem đơn của mình
    if not is_manager and tam_tru.cccd != user_profile.cccd_id:
        messages.error(request, 'Bạn không có quyền xem đơn này!')
        return redirect('users:tam_tru_tam_vang')
    
    # Xử lý phê duyệt (chỉ cán bộ)
    if request.method == 'POST' and is_manager:
        action = request.POST.get('action')
        ghi_chu = request.POST.get('ghi_chu', '')
        
        if action == 'approve':
            tam_tru.trang_thai = 'DaDuyet'
            tam_tru.ghi_chu_can_bo = ghi_chu
            tam_tru.nguoi_duyet = request.user
            tam_tru.ngay_duyet = timezone.now()
            tam_tru.save()
            messages.success(request, 'Đã phê duyệt đơn tạm trú thành công!')
        elif action == 'reject':
            tam_tru.trang_thai = 'TuChoi'
            tam_tru.ghi_chu_can_bo = ghi_chu
            tam_tru.nguoi_duyet = request.user
            tam_tru.ngay_duyet = timezone.now()
            tam_tru.save()
            messages.success(request, 'Đã từ chối đơn tạm trú!')
        
        return redirect('users:tam_tru_tam_vang')
    
    context = {
        'tam_tru': tam_tru,
        'is_manager': is_manager,
    }
    return render(request, 'users/chi_tiet_tam_tru.html', context)


@login_required
def chi_tiet_tam_vang_view(request, pk):
    """Xem chi tiết đơn tạm vắng (cho cán bộ phê duyệt và người dân xem đơn của mình)"""
    from apps.core.models import TamVang
    from django.utils import timezone
    
    user_profile = request.user.profile
    is_manager = user_profile.role in ['admin', 'citizenship_manager', 'commendation_manager']
    
    tam_vang = TamVang.objects.get(pk=pk)
    
    # Kiểm tra quyền: cán bộ xem tất cả, người dân chỉ xem đơn của mình
    if not is_manager and tam_vang.cccd != user_profile.cccd_id:
        messages.error(request, 'Bạn không có quyền xem đơn này!')
        return redirect('users:tam_tru_tam_vang')
    
    # Xử lý phê duyệt (chỉ cán bộ)
    if request.method == 'POST' and is_manager:
        action = request.POST.get('action')
        ghi_chu = request.POST.get('ghi_chu', '')
        
        if action == 'approve':
            tam_vang.trang_thai = 'DaDuyet'
            tam_vang.ghi_chu_can_bo = ghi_chu
            tam_vang.nguoi_duyet = request.user
            tam_vang.ngay_duyet = timezone.now()
            tam_vang.save()
            messages.success(request, 'Đã phê duyệt đơn tạm vắng thành công!')
        elif action == 'reject':
            tam_vang.trang_thai = 'TuChoi'
            tam_vang.ghi_chu_can_bo = ghi_chu
            tam_vang.nguoi_duyet = request.user
            tam_vang.ngay_duyet = timezone.now()
            tam_vang.save()
            messages.success(request, 'Đã từ chối đơn tạm vắng!')
        
        return redirect('users:tam_tru_tam_vang')
    
    context = {
        'tam_vang': tam_vang,
        'is_manager': is_manager,
    }
    return render(request, 'users/chi_tiet_tam_vang.html', context)


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
