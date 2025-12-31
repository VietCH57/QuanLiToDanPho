# --- ADMIN: Thống kê nhân khẩu ---
from django.shortcuts import render
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
@login_required
def admin_thong_ke_nhan_khau(request):
    if not request.user.profile.role in ['admin', 'citizenship_manager']:
        return HttpResponseForbidden()
    from apps.core.models import ThanhVien
    from django.db.models import Count, Q
    # Thống kê theo giới tính
    gioi_tinh_stats = ThanhVien.objects.values('gioi_tinh').annotate(count=Count('id'))
    # Thống kê theo trạng thái cư trú
    trang_thai_stats = ThanhVien.objects.values('trang_thai').annotate(count=Count('id'))
    # Thống kê theo độ tuổi
    import datetime
    today = datetime.date.today()
    def get_age(birthdate):
        return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    all_tv = ThanhVien.objects.all()
    age_groups = {
        'Mầm non (0-5)': 0,
        'Mẫu giáo (6-7)': 0,
        'Cấp 1 (8-10)': 0,
        'Cấp 2 (11-14)': 0,
        'Cấp 3 (15-17)': 0,
        'Lao động (18-60)': 0,
        'Nghỉ hưu (>60)': 0,
    }
    for tv in all_tv:
        age = get_age(tv.ngay_sinh)
        if age <= 5:
            age_groups['Mầm non (0-5)'] += 1
        elif age <= 7:
            age_groups['Mẫu giáo (6-7)'] += 1
        elif age <= 10:
            age_groups['Cấp 1 (8-10)'] += 1
        elif age <= 14:
            age_groups['Cấp 2 (11-14)'] += 1
        elif age <= 17:
            age_groups['Cấp 3 (15-17)'] += 1
        elif age <= 60:
            age_groups['Lao động (18-60)'] += 1
        else:
            age_groups['Nghỉ hưu (>60)'] += 1
    context = {
        'gioi_tinh_stats': gioi_tinh_stats,
        'trang_thai_stats': trang_thai_stats,
        'age_groups': age_groups,
    }
    return render(request, 'users/admin_thong_ke_nhan_khau.html', context)
# --- ADMIN: Tách hộ ---
@login_required
def admin_tach_ho(request, ho_id):
    if not request.user.profile.role in ['admin', 'citizenship_manager']:
        return HttpResponseForbidden()
    from apps.core.models import HoGiaDinh, ThanhVien, LichSuThayDoiHo
    ho = HoGiaDinh.objects.get(pk=ho_id)
    thanh_vien_trong_ho = ho.thanh_vien_trong_ho.all()
    if request.method == 'POST':
        ids = request.POST.getlist('tach_ids')
        if not ids:
            messages.error(request, 'Vui lòng chọn ít nhất một nhân khẩu để tách!')
        else:
            # Tạo hộ mới
            ma_ho_moi = request.POST.get('ma_ho_moi')
            dia_chi_moi = request.POST.get('dia_chi_moi')
            ho_moi = HoGiaDinh.objects.create(ma_ho=ma_ho_moi, dia_chi=dia_chi_moi)
            # Chuyển các thành viên sang hộ mới
            ThanhVien.objects.filter(id__in=ids).update(ho_gia_dinh=ho_moi)
            # Ghi lịch sử
            LichSuThayDoiHo.objects.create(
                ho_gia_dinh=ho,
                loai_thay_doi='TachHo',
                noi_dung=f'Tách {len(ids)} nhân khẩu sang hộ mới {ma_ho_moi}',
                ngay_thay_doi=timezone.now().date(),
                nguoi_thuc_hien=request.user
            )
            messages.success(request, f'Đã tách hộ thành công!')
            return redirect('users:ho_khau')
    return render(request, 'users/admin_tach_ho.html', {'ho': ho, 'thanh_vien_trong_ho': thanh_vien_trong_ho})
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
    """Trang xem thông tin nhân khẩu (thông tin cá nhân)"""
    from apps.core.models import ThanhVien
    from django.db import models
    
    user_profile = request.user.profile
    is_manager = user_profile.role in ['admin', 'citizenship_manager']
    
    if is_manager:
        # Cán bộ: Xem danh sách tất cả nhân khẩu
        danh_sach_nhan_khau = ThanhVien.objects.select_related('ho_gia_dinh').all().order_by('ho_gia_dinh__ma_ho', '-la_chu_ho')
        
        # Tìm kiếm
        search = request.GET.get('search', '').strip()
        if search:
            danh_sach_nhan_khau = danh_sach_nhan_khau.filter(
                models.Q(ho_ten__icontains=search) |
                models.Q(cccd__icontains=search) |
                models.Q(ho_gia_dinh__ma_ho__icontains=search)
            )
        
        context = {
            'is_manager': is_manager,
            'danh_sach_nhan_khau': danh_sach_nhan_khau,
            'search': search,
        }
        return render(request, 'users/nhan_khau_admin.html', context)
    else:
        # Người dân: Xem thông tin cá nhân
        thanh_vien = None
        try:
            thanh_vien = ThanhVien.objects.select_related('ho_gia_dinh').get(cccd=user_profile.cccd_id)
        except ThanhVien.DoesNotExist:
            pass
        
        context = {
            'is_manager': is_manager,
            'thanh_vien': thanh_vien,
        }
        return render(request, 'users/nhan_khau.html', context)


@login_required
def ho_khau_view(request):
    """Trang quản lý hộ khẩu"""
    from apps.core.models import HoGiaDinh, ThanhVien
    from django.db import models
    
    user_profile = request.user.profile
    is_manager = user_profile.role in ['admin', 'citizenship_manager']
    
    if is_manager:
        # Cán bộ: Xem danh sách tất cả hộ
        danh_sach_ho = HoGiaDinh.objects.select_related('chu_ho').prefetch_related('thanh_vien_trong_ho').all().order_by('ma_ho')
        
        # Tìm kiếm
        search = request.GET.get('search', '').strip()
        if search:
            danh_sach_ho = danh_sach_ho.filter(
                models.Q(ma_ho__icontains=search) |
                models.Q(chu_ho__ho_ten__icontains=search) |
                models.Q(dia_chi__icontains=search)
            )
        
        # Thống kê
        tong_so_ho = danh_sach_ho.count()
        tong_nhan_khau = ThanhVien.objects.filter(trang_thai='ThuongTru').count()
        
        context = {
            'is_manager': is_manager,
            'danh_sach_ho': danh_sach_ho,
            'search': search,
            'tong_so_ho': tong_so_ho,
            'tong_nhan_khau': tong_nhan_khau,
        }
        return render(request, 'users/ho_khau_admin.html', context)
    else:
        # Người dân: Xem sổ hộ khẩu của mình
        thanh_vien = None
        ho_gia_dinh = None
        thanh_vien_trong_ho = []
        
        try:
            thanh_vien = ThanhVien.objects.select_related('ho_gia_dinh__chu_ho').get(cccd=user_profile.cccd_id)
            ho_gia_dinh = thanh_vien.ho_gia_dinh
            # Lấy danh sách thành viên trong hộ, chủ hộ đứng đầu
            thanh_vien_trong_ho = ho_gia_dinh.thanh_vien_trong_ho.all().order_by('-la_chu_ho', 'ngay_sinh')
        except ThanhVien.DoesNotExist:
            pass
        
        context = {
            'is_manager': is_manager,
            'thanh_vien': thanh_vien,
            'ho_gia_dinh': ho_gia_dinh,
            'thanh_vien_trong_ho': thanh_vien_trong_ho,
        }
        return render(request, 'users/ho_khau.html', context)
    
    if is_manager:
        # Cán bộ: Xem danh sách tất cả hộ
        danh_sach_ho = HoGiaDinh.objects.select_related('chu_ho').prefetch_related('thanh_vien_trong_ho').all().order_by('ma_ho')
        
        # Tìm kiếm
        search = request.GET.get('search', '').strip()
        if search:
            danh_sach_ho = danh_sach_ho.filter(
                models.Q(ma_ho__icontains=search) |
                models.Q(chu_ho__ho_ten__icontains=search) |
                models.Q(dia_chi__icontains=search)
            )
        
        # Thống kê
        tong_so_ho = danh_sach_ho.count()
        tong_nhan_khau = ThanhVien.objects.filter(trang_thai='ThuongTru').count()
        
        context = {
            'is_manager': is_manager,
            'danh_sach_ho': danh_sach_ho,
            'search': search,
            'tong_so_ho': tong_so_ho,
            'tong_nhan_khau': tong_nhan_khau,
        }
        return render(request, 'users/ho_khau_admin.html', context)
    else:
        # Người dân: Xem sổ hộ khẩu của mình
        thanh_vien = None
        ho_gia_dinh = None
        thanh_vien_trong_ho = []
        
        try:
            thanh_vien = ThanhVien.objects.select_related('ho_gia_dinh__chu_ho').get(cccd=user_profile.cccd_id)
            ho_gia_dinh = thanh_vien.ho_gia_dinh
            # Lấy danh sách thành viên trong hộ, chủ hộ đứng đầu
            thanh_vien_trong_ho = ho_gia_dinh.thanh_vien_trong_ho.all().order_by('-la_chu_ho', 'ngay_sinh')
        except ThanhVien.DoesNotExist:
            pass
        
        context = {
            'is_manager': is_manager,
            'thanh_vien': thanh_vien,
            'ho_gia_dinh': ho_gia_dinh,
            'thanh_vien_trong_ho': thanh_vien_trong_ho,
        }
        return render(request, 'users/ho_khau.html', context)


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


# --- ADMIN: CRUD nhân khẩu ---
from django.urls import reverse
from django.http import HttpResponseForbidden
from apps.core.models import ThanhVien, HoGiaDinh
from django import forms

class ThanhVienForm(forms.ModelForm):
    class Meta:
        model = ThanhVien
        fields = ['ho_gia_dinh', 'ho_ten', 'bi_danh', 'cccd', 'ngay_sinh', 'noi_sinh', 
                  'nguyen_quan', 'dan_toc', 'gioi_tinh', 'nghe_nghiep', 'noi_lam_viec', 
                  'ngay_cap_cccd', 'noi_cap_cccd', 'ngay_dang_ky_thuong_tru', 
                  'dia_chi_truoc_chuyen_den', 'la_chu_ho', 'quan_he_chu_ho', 'trang_thai']
        widgets = {
            'ngay_sinh': forms.DateInput(attrs={'type': 'date'}),
            'ngay_cap_cccd': forms.DateInput(attrs={'type': 'date'}),
            'ngay_dang_ky_thuong_tru': forms.DateInput(attrs={'type': 'date'}),
            'ho_gia_dinh': forms.Select(attrs={'class': 'form-control'}),
            'ho_ten': forms.TextInput(attrs={'class': 'form-control'}),
            'bi_danh': forms.TextInput(attrs={'class': 'form-control'}),
            'cccd': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '12'}),
            'noi_sinh': forms.TextInput(attrs={'class': 'form-control'}),
            'nguyen_quan': forms.TextInput(attrs={'class': 'form-control'}),
            'dan_toc': forms.TextInput(attrs={'class': 'form-control'}),
            'gioi_tinh': forms.Select(attrs={'class': 'form-control'}),
            'nghe_nghiep': forms.TextInput(attrs={'class': 'form-control'}),
            'noi_lam_viec': forms.TextInput(attrs={'class': 'form-control'}),
            'noi_cap_cccd': forms.TextInput(attrs={'class': 'form-control'}),
            'dia_chi_truoc_chuyen_den': forms.TextInput(attrs={'class': 'form-control'}),
            'quan_he_chu_ho': forms.TextInput(attrs={'class': 'form-control'}),
            'trang_thai': forms.Select(attrs={'class': 'form-control'}),
            'la_chu_ho': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

@login_required
def admin_them_nhan_khau(request):
    if not request.user.profile.role in ['admin', 'citizenship_manager']:
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = ThanhVienForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm nhân khẩu mới!')
            return redirect('users:nhan_khau')
    else:
        form = ThanhVienForm()
    return render(request, 'users/admin_them_nhan_khau.html', {'form': form})

@login_required
def admin_sua_nhan_khau(request, pk):
    if not request.user.profile.role in ['admin', 'citizenship_manager']:
        return HttpResponseForbidden()
    thanh_vien = ThanhVien.objects.get(pk=pk)
    if request.method == 'POST':
        form = ThanhVienForm(request.POST, instance=thanh_vien)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật thông tin nhân khẩu!')
            return redirect('users:nhan_khau')
    else:
        form = ThanhVienForm(instance=thanh_vien)
    return render(request, 'users/admin_sua_nhan_khau.html', {'form': form, 'thanh_vien': thanh_vien})

@login_required
def admin_xoa_nhan_khau(request, pk):
    if not request.user.profile.role in ['admin', 'citizenship_manager']:
        return HttpResponseForbidden()
    thanh_vien = ThanhVien.objects.get(pk=pk)
    if request.method == 'POST':
        thanh_vien.delete()
        messages.success(request, 'Đã xoá nhân khẩu!')
        return redirect('users:nhan_khau')
    return render(request, 'users/admin_xoa_nhan_khau.html', {'thanh_vien': thanh_vien})

@login_required
def admin_them_ho_khau(request):
    if not request.user.profile.role in ['admin', 'citizenship_manager']:
        return HttpResponseForbidden()
    from apps.core.models import HoGiaDinh
    if request.method == 'POST':
        ma_ho = request.POST.get('ma_ho')
        dia_chi = request.POST.get('dia_chi')
        if not ma_ho or not dia_chi:
            messages.error(request, 'Vui lòng nhập đầy đủ thông tin!')
        else:
            HoGiaDinh.objects.create(ma_ho=ma_ho, dia_chi=dia_chi)
            messages.success(request, 'Đã thêm hộ khẩu mới!')
            return redirect('users:ho_khau')
    return render(request, 'users/admin_them_ho_khau.html')

# --- ADMIN: Quản lý phần thưởng ---
@login_required
def admin_quan_ly_phan_thuong(request):
    """Trang quản lý phần thưởng cho admin"""
    if not request.user.profile.role in ['admin', 'citizenship_manager']:
        return HttpResponseForbidden()
    
    from apps.core.models import LichSuPhatThuong, ThongTinHocTap, DanhMucPhanThuong
    from django.db.models import Sum, Count
    
    # Lấy danh sách lịch sử phát thưởng
    lich_su_list = LichSuPhatThuong.objects.select_related(
        'thanh_vien', 'phan_thuong', 'nguoi_cap', 'thong_tin_hoc_tap'
    ).order_by('-ngay_cap_phat')
    
    # Lấy danh sách thành tích chờ duyệt
    thanh_tich_list = ThongTinHocTap.objects.filter(
        trang_thai='ChoDuyet'
    ).select_related('thanh_vien', 'nguoi_tao').order_by('-ngay_tao')
    
    # Lấy danh mục phần thưởng
    danh_muc_list = DanhMucPhanThuong.objects.all()
    
    # Thống kê
    tong_phat_thuong = LichSuPhatThuong.objects.count()
    tong_gia_tri = LichSuPhatThuong.objects.aggregate(
        total=Sum('phan_thuong__gia_tri')
    )['total'] or 0
    
    pending_count = ThongTinHocTap.objects.filter(trang_thai='ChoDuyet').count()
    approved_count = ThongTinHocTap.objects.filter(trang_thai='DaDuyet').count()
    
    context = {
        'lich_su_list': lich_su_list,
        'thanh_tich_list': thanh_tich_list,
        'danh_muc_list': danh_muc_list,
        'tong_phat_thuong': tong_phat_thuong,
        'tong_gia_tri': tong_gia_tri,
        'pending_count': pending_count,
        'approved_count': approved_count,
    }
    
    return render(request, 'users/admin_quan_ly_phan_thuong.html', context)

@login_required
def tao_dot_phat_thuong(request):
    """Tạo đợt phát thưởng theo dịp lễ"""
    if not request.user.profile.role in ['admin', 'citizenship_manager']:
        return HttpResponseForbidden()
    
    if request.method != 'POST':
        return redirect('users:admin_quan_ly_phan_thuong')
    
    from apps.core.models import LichSuPhatThuong, DanhMucPhanThuong
    import requests
    
    loai_dip = request.POST.get('loai_dip')
    phan_thuong_id = request.POST.get('phan_thuong_id')
    dot_phat = request.POST.get('dot_phat')
    so_luong = int(request.POST.get('so_luong', 1))
    ghi_chu = request.POST.get('ghi_chu', '')
    thanh_vien_ids = request.POST.getlist('thanh_vien_ids')
    
    if not thanh_vien_ids:
        messages.error(request, 'Không có thành viên nào được chọn!')
        return redirect('users:admin_quan_ly_phan_thuong')
    
    try:
        phan_thuong = DanhMucPhanThuong.objects.get(id=phan_thuong_id)
        
        # Tạo phát thưởng cho từng thành viên
        created_count = 0
        for tv_id in thanh_vien_ids:
            LichSuPhatThuong.objects.create(
                thanh_vien_id=tv_id,
                phan_thuong=phan_thuong,
                loai_phat_thuong='DipLe',
                so_luong=so_luong,
                dot_phat=dot_phat,
                ghi_chu=ghi_chu,
                nguoi_cap=request.user
            )
            created_count += 1
        
        messages.success(request, f'Đã tạo đợt phát thưởng cho {created_count} người!')
    except Exception as e:
        messages.error(request, f'Có lỗi xảy ra: {str(e)}')
    
    return redirect('users:admin_quan_ly_phan_thuong')

@login_required
def phat_thuong_hoc_tap(request):
    """Phát thưởng cho thành tích học tập đã duyệt"""
    if not request.user.profile.role in ['admin', 'citizenship_manager']:
        return HttpResponseForbidden()
    
    if request.method != 'POST':
        return redirect('users:admin_quan_ly_phan_thuong')
    
    from apps.core.models import LichSuPhatThuong, DanhMucPhanThuong, ThongTinHocTap
    
    phan_thuong_id = request.POST.get('phan_thuong_id')
    dot_phat = request.POST.get('dot_phat')
    ghi_chu = request.POST.get('ghi_chu', '')
    thong_tin_hoc_tap_ids = request.POST.getlist('thong_tin_hoc_tap_ids')
    
    if not thong_tin_hoc_tap_ids:
        messages.error(request, 'Không có thành tích nào được chọn!')
        return redirect('users:admin_quan_ly_phan_thuong')
    
    try:
        phan_thuong = DanhMucPhanThuong.objects.get(id=phan_thuong_id)
        
        # Tạo phát thưởng cho từng thành tích
        created_count = 0
        for tt_id in thong_tin_hoc_tap_ids:
            tt = ThongTinHocTap.objects.get(id=tt_id)
            
            # Tính số lượng vở dựa trên thành tích
            so_luong = 5  # Mặc định
            if tt.thanh_tich in ['HocSinhGioi', 'ThanhTichDacBiet']:
                so_luong = 10
            elif tt.thanh_tich == 'HocSinhTienTien':
                so_luong = 7
            
            LichSuPhatThuong.objects.create(
                thanh_vien=tt.thanh_vien,
                phan_thuong=phan_thuong,
                loai_phat_thuong='HocTap',
                thong_tin_hoc_tap=tt,
                so_luong=so_luong,
                dot_phat=dot_phat,
                ghi_chu=ghi_chu,
                nguoi_cap=request.user
            )
            created_count += 1
        
        messages.success(request, f'Đã phát thưởng học tập cho {created_count} thành tích!')
    except Exception as e:
        messages.error(request, f'Có lỗi xảy ra: {str(e)}')
    
    return redirect('users:admin_quan_ly_phan_thuong')

@login_required
def duyet_thanh_tich(request, thanh_tich_id):
    """Duyệt hoặc từ chối thành tích học tập"""
    if not request.user.profile.role in ['admin', 'citizenship_manager']:
        return HttpResponseForbidden()
    
    if request.method != 'POST':
        return redirect('users:admin_quan_ly_phan_thuong')
    
    from apps.core.models import ThongTinHocTap
    from django.utils import timezone
    
    try:
        tt = ThongTinHocTap.objects.get(id=thanh_tich_id)
        action = request.POST.get('action')
        
        if action == 'approve':
            tt.trang_thai = 'DaDuyet'
            tt.nguoi_duyet = request.user
            tt.ngay_duyet = timezone.now().date()
            tt.save()
            messages.success(request, f'Đã duyệt thành tích của {tt.thanh_vien.ho_ten}!')
        
        elif action == 'reject':
            ly_do = request.POST.get('ly_do_tu_choi', '')
            tt.trang_thai = 'TuChoi'
            tt.nguoi_duyet = request.user
            tt.ngay_duyet = timezone.now().date()
            tt.ly_do_tu_choi = ly_do
            tt.save()
            messages.warning(request, f'Đã từ chối thành tích của {tt.thanh_vien.ho_ten}!')
    
    except Exception as e:
        messages.error(request, f'Có lỗi xảy ra: {str(e)}')
    
    return redirect('users:admin_quan_ly_phan_thuong')

# --- CITIZEN: Gửi thành tích học tập ---
@login_required
def thanh_tich_hoc_tap_view(request):
    """Trang xem và gửi thành tích học tập của citizen"""
    if not hasattr(request.user, 'profile'):
        return HttpResponseForbidden()
    
    from apps.core.models import ThongTinHocTap, ThanhVien
    
    # Tìm thành viên tương ứng với user
    try:
        thanh_vien = ThanhVien.objects.get(cccd=request.user.username)
    except ThanhVien.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin nhân khẩu của bạn!')
        return redirect('users:dashboard')
    
    # Lấy danh sách thành tích của thành viên này
    thanh_tich_list = ThongTinHocTap.objects.filter(
        thanh_vien=thanh_vien
    ).order_by('-ngay_tao')
    
    context = {
        'thanh_tich_list': thanh_tich_list,
        'thanh_vien': thanh_vien,
    }
    
    return render(request, 'users/thanh_tich_hoc_tap.html', context)

@login_required
def gui_thanh_tich(request):
    """Gửi thành tích học tập mới"""
    if request.method != 'POST':
        return redirect('users:thanh_tich_hoc_tap')
    
    from apps.core.models import ThongTinHocTap, ThanhVien
    
    try:
        thanh_vien = ThanhVien.objects.get(cccd=request.user.username)
        
        nam_hoc = request.POST.get('nam_hoc')
        truong = request.POST.get('truong')
        lop = request.POST.get('lop')
        thanh_tich = request.POST.get('thanh_tich')
        minh_chung = request.FILES.get('minh_chung')
        
        if not all([nam_hoc, truong, lop, thanh_tich, minh_chung]):
            messages.error(request, 'Vui lòng điền đầy đủ thông tin!')
            return redirect('users:thanh_tich_hoc_tap')
        
        ThongTinHocTap.objects.create(
            thanh_vien=thanh_vien,
            nam_hoc=nam_hoc,
            truong=truong,
            lop=lop,
            thanh_tich=thanh_tich,
            minh_chung=minh_chung,
            nguoi_tao=request.user
        )
        
        messages.success(request, 'Đã gửi thành tích học tập! Vui lòng chờ duyệt.')
    
    except ThanhVien.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin nhân khẩu của bạn!')
    except Exception as e:
        messages.error(request, f'Có lỗi xảy ra: {str(e)}')
    
    return redirect('users:thanh_tich_hoc_tap')

# --- CITIZEN: Xem phần thưởng của tôi ---
@login_required
def phan_thuong_cua_toi(request):
    """Trang xem phần thưởng đã nhận"""
    if not hasattr(request.user, 'profile'):
        return HttpResponseForbidden()
    
    from apps.core.models import LichSuPhatThuong, ThanhVien
    from django.db.models import Sum, Count
    
    try:
        thanh_vien = ThanhVien.objects.get(cccd=request.user.username)
    except ThanhVien.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin nhân khẩu của bạn!')
        return redirect('users:dashboard')
    
    # Lấy danh sách phần thưởng
    phan_thuong_list = LichSuPhatThuong.objects.filter(
        thanh_vien=thanh_vien
    ).select_related('phan_thuong', 'nguoi_cap').order_by('-ngay_cap_phat')
    
    # Thống kê
    tong_phan_thuong = phan_thuong_list.count()
    tong_gia_tri = sum(pt.tong_gia_tri() for pt in phan_thuong_list)
    so_phan_thuong_hoc_tap = phan_thuong_list.filter(loai_phat_thuong='HocTap').count()
    so_phan_thuong_dip_le = phan_thuong_list.filter(loai_phat_thuong='DipLe').count()
    
    context = {
        'phan_thuong_list': phan_thuong_list,
        'tong_phan_thuong': tong_phan_thuong,
        'tong_gia_tri': tong_gia_tri,
        'so_phan_thuong_hoc_tap': so_phan_thuong_hoc_tap,
        'so_phan_thuong_dip_le': so_phan_thuong_dip_le,
    }
    
    return render(request, 'users/phan_thuong_cua_toi.html', context)
