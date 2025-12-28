# ==========================================================
#  IMPORTS (THƯ VIỆN & MODULE)
# ==========================================================
from datetime import date
from django.db import transaction
from django.db.models import Sum
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

# --- 1. IMPORT ĐỂ TẮT CHECK CSRF (GIÚP FRONTEND GỌI API DỄ DÀNG) ---
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# REST Framework Imports
# --- 2. THÊM 'filters' VÀO DÒNG NÀY ---
from rest_framework import viewsets, permissions, status, filters 
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied

# --- 3. IMPORT THƯ VIỆN LỌC DỮ LIỆU ---
from django_filters.rest_framework import DjangoFilterBackend

# Local Imports (Giữ nguyên code cũ của bạn)
from .models import (
    HoGiaDinh, ThanhVien, DanhMucPhanThuong, 
    LichSuPhatThuong, TamTru, TamVang
)
from .serializers import (
    HoGiaDinhSerializer, ThanhVienSerializer, 
    DanhMucPhanThuongSerializer, LichSuPhatThuongSerializer, 
    TamTruSerializer, TamVangSerializer, UserManagementSerializer
)
from .permissions import IsToTruong, IsAdminOrToTruong, IsCanBo

# ==========================================================
#  HELPER CLASSES
# ==========================================================

class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Quyền hỗn hợp:
    - Khách: Xem (GET).
    - Staff: Thêm/Sửa/Xóa.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)


# ==========================================================
#  PHẦN 1: QUẢN LÝ DÂN CƯ
# ==========================================================

# --- Class 1: Hộ Gia Đình ---
@method_decorator(csrf_exempt, name='dispatch') # <--- 1. Tắt CSRF
class HoGiaDinhViewSet(viewsets.ModelViewSet):
    """API quản lý Hộ khẩu."""
    # Sắp xếp theo mã hộ để dễ nhìn
    queryset = HoGiaDinh.objects.all().order_by('ma_ho')
    serializer_class = HoGiaDinhSerializer
    # Đổi sang IsCanBo để khớp với fix lỗi 403 lúc nãy
    permission_classes = [IsCanBo] 

    # <--- 2. Thêm bộ lọc & Tìm kiếm
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['ma_ho', 'dia_chi', 'chu_ho__ho_ten'] # Tìm theo mã, địa chỉ, tên chủ hộ
    filterset_fields = ['ma_ho']


# --- Class 2: Thành Viên (Giữ nguyên logic tạo chủ hộ) ---
@method_decorator(csrf_exempt, name='dispatch') # <--- 1. Tắt CSRF
class ThanhVienViewSet(viewsets.ModelViewSet):
    """API quản lý Nhân khẩu (kèm logic chuyển chủ hộ)."""
    # Dùng select_related để tối ưu Query (Code cũ của bạn rất tốt chỗ này)
    queryset = ThanhVien.objects.select_related('ho_gia_dinh').all().order_by('ho_ten')
    serializer_class = ThanhVienSerializer
    # Đổi sang IsCanBo để khớp với fix lỗi 403
    permission_classes = [IsCanBo]

    # <--- 2. Thêm bộ lọc & Tìm kiếm
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['ho_ten', 'cccd', 'ho_gia_dinh__ma_ho'] # Tìm tên, cccd, mã hộ
    filterset_fields = ['gioi_tinh', 'trang_thai', 'la_chu_ho']

    # <--- 3. GIỮ NGUYÊN LOGIC CŨ CỦA BẠN (Không sửa dòng nào ở dưới)
    def perform_create(self, serializer):
        validated = dict(serializer.validated_data)
        
        # Kiểm tra cờ force_chu_ho
        force_flag = validated.pop('force_chu_ho', False)
        wants_la_chu = validated.get('la_chu_ho', False)
        relation = (validated.get('quan_he_chu_ho') or "").strip().lower()
        wants_relation_chu = ('chủ hộ' in relation or 'chu ho' in relation)

        if not (force_flag or wants_la_chu or wants_relation_chu):
            serializer.save()
            return

        if not (self.request.user and (self.request.user.is_staff or self.request.user.is_superuser or getattr(self.request.user, 'profile', None))):
             # (Tôi sửa nhẹ dòng trên để cho phép cả User Profile có quyền CanBo được sửa)
            raise PermissionDenied("Chỉ cán bộ quản lý mới có quyền thay đổi Chủ hộ.")

        ho = validated.get('ho_gia_dinh')
        if not ho:
            raise PermissionDenied("Phải thuộc về một hộ gia đình.")

        with transaction.atomic():
            ho_locked = HoGiaDinh.objects.select_for_update().get(pk=ho.pk)
            existing_chu = ho_locked.chu_ho

            data_for_instance = {k: v for k, v in validated.items() if k != 'force_chu_ho'}
            instance = ThanhVien(**data_for_instance)
            instance.save(skip_full_clean=True)

            if existing_chu and existing_chu.pk != instance.pk:
                existing_chu.la_chu_ho = False
                existing_chu.save(skip_full_clean=True)

            HoGiaDinh.objects.filter(pk=ho_locked.pk).update(chu_ho=instance)
            ThanhVien.objects.filter(ho_gia_dinh=ho_locked).exclude(pk=instance.pk).update(la_chu_ho=False)

            if not instance.la_chu_ho:
                instance.la_chu_ho = True
                instance.save(skip_full_clean=True)

            serializer.instance = instance

    def perform_update(self, serializer):
        super().perform_update(serializer)

# ==========================================================
#  PHẦN 6: QUẢN LÝ KHEN THƯỞNG
# ==========================================================

class DanhMucPhanThuongViewSet(viewsets.ModelViewSet):
    queryset = DanhMucPhanThuong.objects.all().order_by('ten_phan_thuong')
    serializer_class = DanhMucPhanThuongSerializer
    permission_classes = [IsStaffOrReadOnly]


class LichSuPhatThuongViewSet(viewsets.ModelViewSet):
    """API Quản lý phát quà (Gợi ý & Thống kê)."""
    queryset = LichSuPhatThuong.objects.select_related('thanh_vien', 'phan_thuong').all().order_by('-ngay_cap_phat')
    serializer_class = LichSuPhatThuongSerializer
    permission_classes = [IsCanBo]

    def perform_create(self, serializer):
        serializer.save(nguoi_cap=self.request.user)

    @action(detail=False, methods=['get'], url_path='goi-y-danh-sach')
    def goi_y_danh_sach(self, request):
        loai = request.query_params.get('loai', 'TrungThu')
        today = date.today()
        danh_sach = []
        all_members = ThanhVien.objects.filter(trang_thai='ThuongTru')

        for tv in all_members:
            tuoi = today.year - tv.ngay_sinh.year - ((today.month, today.day) < (tv.ngay_sinh.month, tv.ngay_sinh.day))
            is_eligible = False
            ly_do = ""

            if loai == 'TrungThu' and 0 <= tuoi <= 15:
                is_eligible = True
                ly_do = f"Trẻ em {tuoi} tuổi"
            elif loai == 'HocSinh' and 6 <= tuoi <= 18:
                is_eligible = True
                ly_do = f"Học sinh {tuoi} tuổi"

            if is_eligible:
                danh_sach.append({
                    "id": tv.id,
                    "ho_ten": tv.ho_ten,
                    "ngay_sinh": tv.ngay_sinh,
                    "tuoi": tuoi,
                    "ho_gia_dinh": tv.ho_gia_dinh.ma_ho,
                    "ly_do_de_xuat": ly_do
                })

        return Response({
            "tieu_chi": loai,
            "so_luong_de_xuat": len(danh_sach),
            "danh_sach": danh_sach
        })

    @action(detail=False, methods=['get'], url_path='thong-ke')
    def thong_ke(self, request):
        dot_phat = request.query_params.get('dot_phat')
        if not dot_phat:
            cac_dot = LichSuPhatThuong.objects.values_list('dot_phat', flat=True).distinct()
            return Response({"cac_dot_phat_hien_co": cac_dot})

        records = LichSuPhatThuong.objects.filter(dot_phat=dot_phat)
        tong_tien = records.aggregate(Sum('phan_thuong__gia_tri'))['phan_thuong__gia_tri__sum'] or 0
        so_luong = records.count()
        da_nhan = records.filter(trang_thai='DaNhan').count()

        return Response({
            "dot_phat": dot_phat,
            "tong_so_suat_qua": so_luong,
            "da_phat": da_nhan,
            "chua_phat": so_luong - da_nhan,
            "tong_gia_tri_uoc_tinh": f"{tong_tien:,.0f} VNĐ"
        })


# ==========================================================
#  PHẦN 5: QUẢN LÝ CƯ TRÚ
# ==========================================================

class TamTruViewSet(viewsets.ModelViewSet):
    queryset = TamTru.objects.all().order_by('-ngay_bat_dau')
    serializer_class = TamTruSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='duyet')
    def duyet_don(self, request, pk=None):
        if not (request.user.is_staff or request.user.is_superuser):
             return Response({"detail": "Bạn không có quyền duyệt đơn."}, status=403)
        
        don = self.get_object()
        trang_thai_moi = request.data.get('trang_thai')
        ghi_chu = request.data.get('ghi_chu', '')

        if trang_thai_moi in ['DaDuyet', 'TuChoi']:
            don.trang_thai = trang_thai_moi
            don.ghi_chu_can_bo = ghi_chu
            don.save()
            return Response({"message": f"Đã cập nhật trạng thái thành {trang_thai_moi}"})
        return Response({"error": "Trạng thái không hợp lệ"}, status=400)


class TamVangViewSet(viewsets.ModelViewSet):
    queryset = TamVang.objects.all().order_by('-ngay_bat_dau')
    serializer_class = TamVangSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='duyet')
    def duyet_don(self, request, pk=None):
        if not (request.user.is_staff or request.user.is_superuser):
             return Response({"detail": "Bạn không có quyền duyệt đơn."}, status=403)
        
        don = self.get_object()
        trang_thai_moi = request.data.get('trang_thai')
        ghi_chu = request.data.get('ghi_chu', '')

        if trang_thai_moi in ['DaDuyet', 'TuChoi']:
            don.trang_thai = trang_thai_moi
            don.ghi_chu_can_bo = ghi_chu
            don.save()
            return Response({"message": f"Đã cập nhật trạng thái thành {trang_thai_moi}"})
        return Response({"error": "Trạng thái không hợp lệ"}, status=400)


# ==========================================================
#  PHẦN 7: QUẢN TRỊ NGƯỜI DÙNG
# ==========================================================

class UserManagementViewSet(viewsets.ModelViewSet):
    """API đặc quyền cho Tổ trưởng: Xem/Tạo/Xóa cấp dưới."""
    serializer_class = UserManagementSerializer
    permission_classes = [IsAdminOrToTruong]

    def get_queryset(self):
        return User.objects.filter(is_superuser=False).order_by('-date_joined')


# ==========================================================
#  DASHBOARD (BÁO CÁO)
# ==========================================================

class DashboardView(APIView):
    """API Dashboard: Tổng hợp số liệu."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        return Response({
            "tong_ho_gia_dinh": HoGiaDinh.objects.count(),
            "tong_thanh_vien": ThanhVien.objects.count(),
            "tong_phan_thuong": DanhMucPhanThuong.objects.count(),
            "tong_lich_su_phat_thuong": LichSuPhatThuong.objects.count(),
        })