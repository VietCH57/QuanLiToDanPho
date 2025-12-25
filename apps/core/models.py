from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

# Lấy model User hiện hành của hệ thống (thường là auth.User)
User = get_user_model()

# ==========================================================
#  PHẦN 1: QUẢN LÝ HỘ GIA ĐÌNH & NHÂN KHẨU
#  (Nghiệp vụ cốt lõi: Quản lý dân cư)
# ==========================================================

class HoGiaDinh(models.Model):
    """
    Model đại diện cho Sổ Hộ Khẩu.
    - Lưu trữ thông tin chung của hộ.
    - Một hộ chỉ có duy nhất một Chủ hộ tại một thời điểm.
    """
    ma_ho = models.CharField(max_length=10, unique=True, verbose_name="Mã Hộ")
    dia_chi = models.CharField(max_length=255, verbose_name="Địa Chỉ")
    
    # Liên kết 1-1 với Thành viên: Đảm bảo tính nhất quán (1 hộ - 1 chủ)
    # on_delete=SET_NULL: Nếu chủ hộ bị xóa, hộ này tạm thời mất chủ (null) chứ không bị xóa theo.
    chu_ho = models.OneToOneField(
        'ThanhVien',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ho_lam_chu',
        verbose_name="Chủ Hộ"
    )

    def __str__(self):
        return f"Hộ: {self.ma_ho} - {self.dia_chi}"

    class Meta:
        verbose_name_plural = "Hộ Gia Đình"


class ThanhVien(models.Model):
    """
    Model đại diện cho Nhân Khẩu (Thành viên trong hộ).
    - Chứa logic quan trọng về chuyển đổi chủ hộ.
    """
    # Các lựa chọn cố định (Choices) giúp chuẩn hóa dữ liệu đầu vào
    GIOI_TINH = (('Nam', 'Nam'), ('Nu', 'Nữ'), ('Khac', 'Khác'))
    TRANG_THAI = (('ThuongTru', 'Thường trú'), ('TamTru', 'Tạm trú'), ('ChuyenDi', 'Chuyển đi'))

    # --- KHÓA NGOẠI & LIÊN KẾT ---
    # Liên kết với User: Cho phép người dân đăng nhập (nếu có tài khoản)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='thanh_vien'
    )
    
    # Liên kết n-1 với Hộ gia đình: Một hộ có nhiều thành viên
    ho_gia_dinh = models.ForeignKey(
        HoGiaDinh,
        on_delete=models.CASCADE,
        related_name='thanh_vien_trong_ho',
        verbose_name="Hộ Gia Đình"
    )
    
    # --- THÔNG TIN CÁ NHÂN ---
    ho_ten = models.CharField(max_length=100, verbose_name="Họ Tên")
    cccd = models.CharField(max_length=12, unique=True, blank=True, null=True, verbose_name="CCCD")
    ngay_sinh = models.DateField(verbose_name="Ngày Sinh")
    gioi_tinh = models.CharField(max_length=10, choices=GIOI_TINH, blank=True, null=True, verbose_name="Giới tính")
    
    # --- VAI TRÒ TRONG HỘ ---
    quan_he_chu_ho = models.CharField(max_length=50, blank=True, verbose_name="Quan hệ với chủ hộ")
    la_chu_ho = models.BooleanField(default=False, verbose_name="Là chủ hộ")
    trang_thai = models.CharField(max_length=20, choices=TRANG_THAI, default='ThuongTru', verbose_name="Trạng thái cư trú")

    def __str__(self):
        return f"{self.ho_ten} (Hộ {self.ho_gia_dinh.ma_ho})"

    def save(self, *args, skip_full_clean=False, **kwargs):
        """
        LOGIC QUAN TRỌNG: Tự động xử lý khi thay đổi Chủ Hộ.
        Khi một thành viên được đánh dấu là 'la_chu_ho = True':
        1. Hệ thống tự động gán quan hệ là 'Chủ hộ'.
        2. Cập nhật bảng HoGiaDinh để trỏ tới thành viên này.
        3. Tước bỏ quyền chủ hộ của tất cả thành viên khác trong cùng hộ.
        Sử dụng transaction.atomic() để đảm bảo tất cả các bước trên thành công cùng lúc, tránh lỗi dữ liệu.
        """
        # Bước 1: Chuẩn hóa dữ liệu text
        if self.la_chu_ho:
            self.quan_he_chu_ho = "Chủ hộ"
        
        # Bước 2: Thực thi an toàn với Transaction
        with transaction.atomic():
            # Lưu bản ghi hiện tại trước
            super().save(*args, **kwargs) 
            
            # Nếu người này là chủ hộ, thực hiện logic chuyển đổi
            if self.la_chu_ho and self.ho_gia_dinh_id:
                # A. Cập nhật bảng Hộ Gia Đình: Trỏ chủ hộ về người này
                HoGiaDinh.objects.filter(pk=self.ho_gia_dinh_id).update(chu_ho=self.pk)
                
                # B. Reset các thành viên cũ: Đảm bảo trong hộ không còn ai khác là chủ hộ
                ThanhVien.objects.filter(ho_gia_dinh_id=self.ho_gia_dinh_id)\
                    .exclude(pk=self.pk).update(la_chu_ho=False)

    class Meta:
        verbose_name_plural = "Thành Viên"


# ==========================================================
#  PHẦN 6: QUẢN LÝ KHEN THƯỞNG (QUỸ KHUYẾN HỌC)
#  (Nghiệp vụ: Quản lý quà tặng dịp lễ, tết, học sinh giỏi)
# ==========================================================

class DanhMucPhanThuong(models.Model):
    """
    Danh mục định nghĩa các loại phần thưởng.
    Ví dụ: Vở (5k), Bánh kẹo (20k), Tiền mặt (50k)...
    """
    ten_phan_thuong = models.CharField(max_length=150, unique=True, verbose_name="Tên phần thưởng")
    mo_ta = models.TextField(blank=True, verbose_name="Mô tả")
    gia_tri = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Giá trị (VNĐ)")

    def __str__(self):
        return f"{self.ten_phan_thuong} ({self.gia_tri:,.0f}đ)"
    
    class Meta:
        verbose_name_plural = "Danh Mục Phần Thưởng"


class LichSuPhatThuong(models.Model):
    """
    Lưu vết lịch sử phát quà cho từng cá nhân.
    - Hỗ trợ thống kê tài chính theo 'dot_phat'.
    - Hỗ trợ lưu ảnh minh chứng (giấy khen) để làm bằng chứng (audit).
    """
    TRANG_THAI_NHAN = (('ChuaNhan', 'Chưa nhận'), ('DaNhan', 'Đã nhận'))

    thanh_vien = models.ForeignKey(ThanhVien, on_delete=models.CASCADE, related_name='lich_su_nhan_thuong', verbose_name="Người nhận")
    phan_thuong = models.ForeignKey(DanhMucPhanThuong, on_delete=models.CASCADE, verbose_name="Phần thưởng")
    
    # Các trường phục vụ nghiệp vụ Báo cáo & Minh chứng
    dot_phat = models.CharField(max_length=100, verbose_name="Đợt phát (VD: Trung Thu 2025)")
    minh_chung = models.ImageField(upload_to='minh_chung/', blank=True, null=True, verbose_name="Ảnh minh chứng (Giấy khen)")
    trang_thai = models.CharField(max_length=20, choices=TRANG_THAI_NHAN, default='ChuaNhan', verbose_name="Trạng thái")
    
    # Metadata (Thông tin quản trị)
    ngay_cap_phat = models.DateField(auto_now_add=True, verbose_name="Ngày tạo")
    nguoi_cap = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Cán bộ thực hiện")
    ghi_chu = models.TextField(blank=True, verbose_name="Ghi chú")

    def __str__(self):
        return f"{self.dot_phat}: {self.thanh_vien.ho_ten}"

    class Meta:
        verbose_name_plural = "Lịch Sử Phát Thưởng"


# ==========================================================
#  PHẦN 7: QUẢN LÝ USER PROFILE (PHÂN QUYỀN & BẢO MẬT)
#  (Nghiệp vụ: Quản trị hệ thống)
# ==========================================================

class UserProfile(models.Model):
    """
    Mở rộng bảng User mặc định của Django.
    Mục đích: Lưu thêm 'Vai trò' (Role) để phân quyền chi tiết.
    """
    ROLE_CHOICES = (
        ('TO_TRUONG', 'Tổ trưởng'),
        ('TO_PHO', 'Tổ phó'),
        ('CAN_BO_NHAN_KHAU', 'Cán bộ nhân khẩu'),
        ('CAN_BO_HANH_CHINH', 'Cán bộ hành chính'),
        ('NGUOI_DAN', 'Người dân'),
    )
    # OneToOne với User: Mỗi tài khoản chỉ có 1 Profile
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='NGUOI_DAN', verbose_name="Vai trò")
    
    # Cho phép liên kết tài khoản này với một hộ gia đình cụ thể (dành cho Tổ trưởng/Người dân)
    ho_gia_dinh = models.ForeignKey(HoGiaDinh, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Thuộc hộ")

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


# ==========================================================
#  PHẦN 5: QUẢN LÝ TẠM TRÚ - TẠM VẮNG
#  (Nghiệp vụ: Biến động dân cư)
# ==========================================================

class TamTru(models.Model):
    """
    Đơn xin Tạm Trú (người nơi khác đến ở).
    Quy trình: Người dân/Cán bộ tạo đơn -> Trạng thái 'ChoDuyet' -> Tổ trưởng duyệt 'DaDuyet'.
    """
    TRANG_THAI_DUYET = (('ChoDuyet', 'Chờ duyệt'), ('DaDuyet', 'Đã duyệt'), ('TuChoi', 'Từ chối'))

    thanh_vien = models.ForeignKey(ThanhVien, on_delete=models.CASCADE, related_name='don_tam_tru', verbose_name="Người đăng ký")
    
    # Thông tin chi tiết tờ khai
    dia_chi_thuong_tru_goc = models.CharField(max_length=255, verbose_name="Đ/C Thường trú gốc")
    dia_chi_tam_tru = models.CharField(max_length=255, verbose_name="Đ/C Tạm trú tại đây")
    ly_do = models.TextField(verbose_name="Lý do")
    ngay_bat_dau = models.DateField(verbose_name="Ngày bắt đầu")
    ngay_ket_thuc = models.DateField(null=True, blank=True, verbose_name="Ngày kết thúc")
    
    # Quản lý trạng thái duyệt
    trang_thai = models.CharField(max_length=20, choices=TRANG_THAI_DUYET, default='ChoDuyet', verbose_name="Trạng thái")
    ghi_chu_can_bo = models.TextField(blank=True, verbose_name="Ý kiến cán bộ")

    def __str__(self):
        return f"Tạm trú: {self.thanh_vien.ho_ten}"
    
    class Meta: 
        verbose_name_plural = "Đơn Tạm Trú"


class TamVang(models.Model):
    """
    Đơn xin Tạm Vắng (người địa phương đi nơi khác).
    Quy trình tương tự Tạm Trú.
    """
    TRANG_THAI_DUYET = (('ChoDuyet', 'Chờ duyệt'), ('DaDuyet', 'Đã duyệt'), ('TuChoi', 'Từ chối'))

    thanh_vien = models.ForeignKey(ThanhVien, on_delete=models.CASCADE, related_name='don_tam_vang', verbose_name="Người đăng ký")
    
    # Thông tin chi tiết tờ khai
    noi_den = models.CharField(max_length=255, verbose_name="Nơi chuyển đến")
    ly_do = models.TextField(verbose_name="Lý do")
    ngay_bat_dau = models.DateField(verbose_name="Ngày đi")
    ngay_ket_thuc = models.DateField(null=True, blank=True, verbose_name="Ngày về dự kiến")
    
    # Quản lý trạng thái duyệt
    trang_thai = models.CharField(max_length=20, choices=TRANG_THAI_DUYET, default='ChoDuyet', verbose_name="Trạng thái")
    ghi_chu_can_bo = models.TextField(blank=True, verbose_name="Ý kiến cán bộ")

    def __str__(self):
        return f"Tạm vắng: {self.thanh_vien.ho_ten}"
    
    class Meta: 
        verbose_name_plural = "Đơn Tạm Vắng"