from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    HoGiaDinh, ThanhVien, DanhMucPhanThuong, 
    LichSuPhatThuong, TamTru, TamVang
)
from apps.users.models import UserProfile

# ==========================================================
#  NHÓM 1: HỘ GIA ĐÌNH & THÀNH VIÊN
# ==========================================================

class ThanhVienSerializer(serializers.ModelSerializer):
    """
    Serializer cho Nhân khẩu.
    - Hỗ trợ field 'force_chu_ho' (write-only) để client yêu cầu chuyển chủ hộ.
    - Flatten tên chủ hộ để hiển thị dễ dàng hơn.
    """
    # Write-only: Chỉ dùng khi Client gửi lên (POST/PUT), không hiển thị khi GET
    force_chu_ho = serializers.BooleanField(write_only=True, required=False, default=False)
    
    # Hiển thị thêm thông tin hộ (Optional)
    ten_ho_gia_dinh = serializers.CharField(source='ho_gia_dinh.ma_ho', read_only=True)
    tuoi = serializers.SerializerMethodField()

    class Meta:
        model = ThanhVien
        fields = [
            'id', 'ho_gia_dinh', 'ten_ho_gia_dinh',
            'ho_ten', 'bi_danh', 'cccd', 'ngay_sinh', 'tuoi', 
            'noi_sinh', 'nguyen_quan', 'dan_toc', 'gioi_tinh',
            'nghe_nghiep', 'noi_lam_viec',
            'ngay_cap_cccd', 'noi_cap_cccd',
            'ngay_dang_ky_thuong_tru', 'dia_chi_truoc_chuyen_den',
            'quan_he_chu_ho', 'la_chu_ho', 'trang_thai',
            'ngay_chuyen_di', 'noi_chuyen_den', 'ghi_chu_thay_doi',
            'force_chu_ho', # Control field
        ]
        read_only_fields = ['id', 'tuoi']
    
    def get_tuoi(self, obj):
        from datetime import date
        today = date.today()
        return today.year - obj.ngay_sinh.year - (
            (today.month, today.day) < (obj.ngay_sinh.month, obj.ngay_sinh.day)
        )


class HoGiaDinhSerializer(serializers.ModelSerializer):
    """
    Serializer cho Hộ khẩu.
    - Bao gồm danh sách thành viên (Nested) để xem chi tiết hộ tiện lợi.
    """
    # Nested Serializer: Hiển thị luôn danh sách thành viên bên trong object Hộ
    thanh_vien_trong_ho = ThanhVienSerializer(many=True, read_only=True)
    
    # Hiển thị tên chủ hộ thay vì chỉ hiện ID
    ten_chu_ho = serializers.CharField(source='chu_ho.ho_ten', read_only=True)

    class Meta:
        model = HoGiaDinh
        fields = ['id', 'ma_ho', 'dia_chi', 'chu_ho', 'ten_chu_ho', 'thanh_vien_trong_ho']
        read_only_fields = ['id', 'chu_ho', 'thanh_vien_trong_ho']


# ==========================================================
#  NHÓM 2: QUẢN LÝ KHEN THƯỞNG
# ==========================================================

class DanhMucPhanThuongSerializer(serializers.ModelSerializer):
    class Meta:
        model = DanhMucPhanThuong
        fields = ['id', 'ten_phan_thuong', 'mo_ta', 'gia_tri']
        read_only_fields = ['id']


class LichSuPhatThuongSerializer(serializers.ModelSerializer):
    """
    Serializer cho lịch sử phát quà.
    - Flatten dữ liệu (lấy tên thành viên, tên quà) để Frontend hiển thị bảng dễ dàng.
    """
    # Lấy thông tin chi tiết từ bảng liên kết (Foreign Key)
    ten_thanh_vien = serializers.CharField(source='thanh_vien.ho_ten', read_only=True)
    ten_phan_thuong = serializers.CharField(source='phan_thuong.ten_phan_thuong', read_only=True)
    gia_tri_phan_thuong = serializers.DecimalField(source='phan_thuong.gia_tri', max_digits=10, decimal_places=0, read_only=True)

    class Meta:
        model = LichSuPhatThuong
        fields = [
            'id', 'thanh_vien', 'ten_thanh_vien', 
            'phan_thuong', 'ten_phan_thuong', 'gia_tri_phan_thuong',
            'dot_phat', 'minh_chung', 'trang_thai',
            'ngay_cap_phat', 'nguoi_cap', 'ghi_chu'
        ]
        read_only_fields = ['id', 'ngay_cap_phat', 'nguoi_cap']


# ==========================================================
#  NHÓM 3: QUẢN LÝ CƯ TRÚ (TẠM TRÚ / TẠM VẮNG)
# ==========================================================

class TamTruSerializer(serializers.ModelSerializer):
    ten_nguoi_dang_ky = serializers.CharField(source='thanh_vien.ho_ten', read_only=True)

    class Meta:
        model = TamTru
        fields = '__all__'
        read_only_fields = ['id', 'trang_thai', 'ghi_chu_can_bo']


class TamVangSerializer(serializers.ModelSerializer):
    ten_nguoi_dang_ky = serializers.CharField(source='thanh_vien.ho_ten', read_only=True)

    class Meta:
        model = TamVang
        fields = '__all__'
        read_only_fields = ['id', 'trang_thai', 'ghi_chu_can_bo']


# ==========================================================
#  NHÓM 4: QUẢN TRỊ USER (SYSTEM)
# ==========================================================

class UserManagementSerializer(serializers.ModelSerializer):
    """
    Serializer đặc biệt để tạo User kèm Profile (Role).
    """
    # Lấy danh sách Role trực tiếp từ Model để đảm bảo nhất quán (DRY)
    role = serializers.ChoiceField(choices=UserProfile.ROLE_CHOICES, write_only=True)
    
    # Hiển thị role hiện tại khi GET
    current_role = serializers.CharField(source='profile.role', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role', 'current_role']
        extra_kwargs = {'password': {'write_only': True}} # Không bao giờ trả về password hash

    def create(self, validated_data):
        # 1. Tách role ra khỏi dữ liệu tạo User
        role = validated_data.pop('role', 'NGUOI_DAN')
        password = validated_data.pop('password')
        
        # 2. Tạo User chuẩn của Django (tự động hash password)
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        
        # 3. Cập nhật Profile (Profile đã được tạo tự động bởi Signal, ta chỉ update role)
        if hasattr(user, 'profile'):
            user.profile.role = role
            user.profile.save()
            
        return user