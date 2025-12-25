from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

# Import tất cả Models cần quản lý
from .models import (
    HoGiaDinh,
    ThanhVien,
    DanhMucPhanThuong,
    LichSuPhatThuong,
    TamTru,
    TamVang
)
from apps.users.models import UserProfile

# ==========================================================
#  PHẦN 1: CẤU HÌNH HIỂN THỊ PHỤ (INLINES)
#  (Hiển thị bảng con bên trong bảng cha)
# ==========================================================

class ThanhVienInline(admin.TabularInline):
    """
    Cho phép xem và sửa nhanh danh sách thành viên 
    ngay trong giao diện chi tiết của một Hộ Gia Đình.
    """
    model = ThanhVien
    extra = 0  # Không hiển thị các dòng trống thừa thãi
    fields = ('ho_ten', 'ngay_sinh', 'quan_he_chu_ho', 'la_chu_ho')
    readonly_fields = ()
    show_change_link = True # Có nút bấm để nhảy sang trang sửa chi tiết thành viên


# ==========================================================
#  PHẦN 2: QUẢN LÝ HỘ GIA ĐÌNH
# ==========================================================

@admin.register(HoGiaDinh)
class HoGiaDinhAdmin(admin.ModelAdmin):
    list_display = ('ma_ho', 'chu_ho_hien_thi', 'dia_chi')
    search_fields = ('ma_ho', 'dia_chi')
    inlines = [ThanhVienInline]
    # Tối ưu database: load sẵn thông tin chủ hộ để tránh lỗi N+1 queries
    list_select_related = ('chu_ho',)

    def chu_ho_hien_thi(self, obj):
        """
        Custom field: Hiển thị tên chủ hộ.
        Logic: Nếu cột chu_ho chưa set (do lỗi cũ), thử tìm fallback trong danh sách thành viên.
        """
        if obj.chu_ho:
            return obj.chu_ho.ho_ten
        
        # Fallback: tìm thành viên có cờ la_chu_ho=True
        tv = obj.thanh_vien_trong_ho.filter(la_chu_ho=True).first()
        return tv.ho_ten if tv else "Chưa có"
    
    chu_ho_hien_thi.short_description = "Chủ Hộ"


# ==========================================================
#  PHẦN 3: QUẢN LÝ THÀNH VIÊN & LOGIC CHUYỂN CHỦ HỘ
#  (Phần phức tạp nhất: Xử lý Transaction an toàn)
# ==========================================================

@admin.action(description='Đặt/Chuyển thành Chủ Hộ (cho người được chọn)')
def make_chu_ho(modeladmin, request, queryset):
    """
    Action đặc biệt: Xử lý việc chuyển chủ hộ một cách an toàn (Atomic).
    Quy trình:
    1. Khóa bản ghi Hộ gia đình để tránh xung đột.
    2. Gỡ bỏ chủ hộ cũ (nếu có).
    3. Thiết lập người được chọn làm chủ hộ mới.
    4. Cập nhật lại các liên kết trong database.
    """
    success_count = 0
    for tv in queryset:
        try:
            with transaction.atomic():
                if not tv.ho_gia_dinh:
                    messages.error(request, f"Bỏ qua {tv.ho_ten}: Chưa thuộc về hộ nào.")
                    continue

                # Lock dòng HoGiaDinh để không ai sửa đổi trong lúc code này chạy
                ho_locked = HoGiaDinh.objects.select_for_update().get(pk=tv.ho_gia_dinh.pk)
                existing_chu_ho = ho_locked.chu_ho

                # Bước 1: Nếu đã có chủ hộ khác -> Phế truất
                if existing_chu_ho and existing_chu_ho.pk != tv.pk:
                    existing_chu_ho.la_chu_ho = False
                    existing_chu_ho.save(skip_full_clean=True)

                # Bước 2: Sắc phong chủ hộ mới
                tv.la_chu_ho = True
                # Tự động điền "Chủ hộ" vào quan hệ nếu đang trống
                if not tv.quan_he_chu_ho or 'chủ' not in (tv.quan_he_chu_ho or '').lower():
                    tv.quan_he_chu_ho = 'Chủ hộ'
                tv.save(skip_full_clean=True)

                # Bước 3: Cập nhật pointer trong bảng HoGiaDinh
                HoGiaDinh.objects.filter(pk=ho_locked.pk).update(chu_ho=tv)

                # Bước 4: Dọn dẹp lại lần cuối (đảm bảo ko còn ai khác là chủ hộ)
                ThanhVien.objects.filter(ho_gia_dinh=ho_locked).exclude(pk=tv.pk).update(la_chu_ho=False)

            success_count += 1
        except Exception as e:
            messages.error(request, f"Lỗi khi xử lý {tv.ho_ten}: {e}")

    if success_count:
        messages.success(request, f"Đã chuyển thành công {success_count} chủ hộ mới.")


@admin.register(ThanhVien)
class ThanhVienAdmin(admin.ModelAdmin):
    list_display = ('ho_ten', 'ho_gia_dinh', 'quan_he_chu_ho', 'la_chu_ho')
    list_filter = ('ho_gia_dinh', 'la_chu_ho')
    search_fields = ('ho_ten', 'quan_he_chu_ho', 'cccd')
    
    # Gắn action vừa viết ở trên vào menu dropdown
    actions = [make_chu_ho] 
    list_select_related = ('ho_gia_dinh',)

    def save_model(self, request, obj, form, change):
        """
        Override hàm lưu để kiểm tra logic nghiệp vụ (Validation):
        - Ngăn chặn việc sửa thủ công 'Là chủ hộ' nếu hộ đó đã có chủ khác.
        - Bắt buộc dùng Action 'make_chu_ho' để hệ thống xử lý logic chuyển đổi phức tạp.
        """
        # Chuẩn hóa text quan hệ (bỏ khoảng trắng, chữ hoa/thường)
        relation = (obj.quan_he_chu_ho or "").strip()
        relation_norm = relation.lower()
        is_relation_chu = ('chủ hộ' in relation_norm) or ('chu ho' in relation_norm)

        # 1. Tự động đồng bộ Text <-> Checkbox
        if is_relation_chu:
            obj.la_chu_ho = True
            obj.quan_he_chu_ho = 'Chủ hộ'
        
        if obj.la_chu_ho and not is_relation_chu:
            if not obj.quan_he_chu_ho: # Nếu để trống mà tick chủ hộ -> Tự điền
                obj.quan_he_chu_ho = 'Chủ hộ'

        # 2. Validate logic: "Một nước không thể có 2 vua"
        if obj.ho_gia_dinh:
            existing = obj.ho_gia_dinh.chu_ho
            
            # Nếu hộ đã có chủ, và chủ đó KHÔNG PHẢI là người đang sửa
            if existing and existing.pk and existing.pk != (obj.pk or None):
                # Nếu người dùng cố tình tick chọn làm chủ hộ mới bằng tay
                if is_relation_chu or obj.la_chu_ho:
                    raise ValidationError(
                        "LỖI: Hộ này đã có chủ hộ khác. "
                        "Vui lòng dùng chức năng 'Đặt/Chuyển thành Chủ Hộ' (trên thanh Action) để hệ thống xử lý chuyển đổi an toàn."
                    )

        # 3. Lưu an toàn với Transaction
        try:
            with transaction.atomic():
                super().save_model(request, obj, form, change)
        except IntegrityError:
            raise ValidationError("Xung đột dữ liệu. Vui lòng tải lại trang.")


# ==========================================================
#  PHẦN 4: QUẢN LÝ KHEN THƯỞNG
# ==========================================================

@admin.register(DanhMucPhanThuong)
class DanhMucPhanThuongAdmin(admin.ModelAdmin):
    list_display = ('ten_phan_thuong', 'gia_tri')
    search_fields = ('ten_phan_thuong',)


@admin.register(LichSuPhatThuong)
class LichSuPhatThuongAdmin(admin.ModelAdmin):
    list_display = ('thanh_vien', 'phan_thuong', 'ngay_cap_phat', 'nguoi_cap')
    list_filter = ('ngay_cap_phat', 'phan_thuong')
    search_fields = ('thanh_vien__ho_ten',)


# ==========================================================
#  PHẦN 5: QUẢN LÝ CƯ TRÚ (TẠM TRÚ / TẠM VẮNG)
# ==========================================================

@admin.register(TamTru)
class TamTruAdmin(admin.ModelAdmin):
    list_display = ('thanh_vien', 'dia_chi_tam_tru', 'ngay_bat_dau', 'trang_thai')
    list_filter = ('trang_thai', 'ngay_bat_dau')
    search_fields = ('thanh_vien__ho_ten', 'dia_chi_tam_tru')


@admin.register(TamVang)
class TamVangAdmin(admin.ModelAdmin):
    list_display = ('thanh_vien', 'noi_den', 'ngay_bat_dau', 'trang_thai')
    list_filter = ('trang_thai',)
    search_fields = ('thanh_vien__ho_ten', 'noi_den')


# ==========================================================
#  PHẦN 6: QUẢN TRỊ NGƯỜI DÙNG (USER ROLES)
# ==========================================================

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    # Tính năng hay: Cho phép sửa vai trò (Role) ngay tại danh sách
    # giúp Tổ trưởng cấp quyền nhanh mà không cần bấm vào chi tiết
    list_editable = ('role',) 
    search_fields = ('user__username',)