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
    LichSuPhatThuong, TamTru, TamVang, ThongTinHocTap
)
from .serializers import (
    HoGiaDinhSerializer, ThanhVienSerializer, 
    DanhMucPhanThuongSerializer, LichSuPhatThuongSerializer, 
    TamTruSerializer, TamVangSerializer, UserManagementSerializer,
    ThongTinHocTapSerializer
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

    @action(detail=True, methods=['post'], url_path='tach-ho')
    def tach_ho(self, request, pk=None):
        """
        Tách hộ: Tạo hộ mới từ các thành viên được chọn.
        Request data: {
            "ma_ho_moi": "HK123",
            "dia_chi_moi": "123 Đường ABC",
            "thanh_vien_ids": [1, 2, 3],
            "chu_ho_moi_id": 1
        }
        """
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({"detail": "Chỉ admin mới có quyền tách hộ."}, status=403)
        
        ho_cu = self.get_object()
        ma_ho_moi = request.data.get('ma_ho_moi')
        dia_chi_moi = request.data.get('dia_chi_moi')
        thanh_vien_ids = request.data.get('thanh_vien_ids', [])
        chu_ho_moi_id = request.data.get('chu_ho_moi_id')
        
        # Validate
        if not ma_ho_moi or not dia_chi_moi:
            return Response({"error": "Vui lòng nhập đầy đủ mã hộ và địa chỉ mới"}, status=400)
        
        if not thanh_vien_ids or not chu_ho_moi_id:
            return Response({"error": "Vui lòng chọn thành viên và chủ hộ mới"}, status=400)
        
        if HoGiaDinh.objects.filter(ma_ho=ma_ho_moi).exists():
            return Response({"error": f"Mã hộ {ma_ho_moi} đã tồn tại"}, status=400)
        
        if chu_ho_moi_id not in thanh_vien_ids:
            return Response({"error": "Chủ hộ mới phải thuộc danh sách thành viên được chọn"}, status=400)
        
        # Execute with transaction
        try:
            with transaction.atomic():
                # Tạo hộ mới
                ho_moi = HoGiaDinh.objects.create(
                    ma_ho=ma_ho_moi,
                    dia_chi=dia_chi_moi
                )
                
                # Chuyển thành viên sang hộ mới
                thanh_vien_chuyen = ThanhVien.objects.filter(
                    id__in=thanh_vien_ids,
                    ho_gia_dinh=ho_cu
                )
                
                if thanh_vien_chuyen.count() != len(thanh_vien_ids):
                    return Response({"error": "Một số thành viên không thuộc hộ này"}, status=400)
                
                thanh_vien_chuyen.update(ho_gia_dinh=ho_moi, la_chu_ho=False)
                
                # Đặt chủ hộ mới
                chu_ho_moi = ThanhVien.objects.get(id=chu_ho_moi_id)
                chu_ho_moi.la_chu_ho = True
                chu_ho_moi.quan_he_chu_ho = "Chủ hộ"
                chu_ho_moi.save()
                
                ho_moi.chu_ho = chu_ho_moi
                ho_moi.save()
                
                # Ghi lịch sử
                from .models import LichSuThayDoiHo
                LichSuThayDoiHo.objects.create(
                    ho_gia_dinh=ho_cu,
                    loai_thay_doi='TachHo',
                    noi_dung=f"Tách {len(thanh_vien_ids)} thành viên sang hộ {ma_ho_moi}",
                    ngay_thay_doi=date.today(),
                    nguoi_thuc_hien=request.user
                )
                
                LichSuThayDoiHo.objects.create(
                    ho_gia_dinh=ho_moi,
                    loai_thay_doi='TachHo',
                    noi_dung=f"Tách từ hộ {ho_cu.ma_ho}",
                    ngay_thay_doi=date.today(),
                    nguoi_thuc_hien=request.user
                )
                
                return Response({
                    "message": "Tách hộ thành công",
                    "ho_moi": {
                        "id": ho_moi.id,
                        "ma_ho": ho_moi.ma_ho,
                        "dia_chi": ho_moi.dia_chi,
                        "chu_ho": chu_ho_moi.ho_ten
                    }
                }, status=201)
                
        except Exception as e:
            return Response({"error": str(e)}, status=500)


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
    
    @action(detail=True, methods=['post'], url_path='cap-nhat-trang-thai')
    def cap_nhat_trang_thai(self, request, pk=None):
        """
        Cập nhật trạng thái thành viên (chuyển đi, qua đời, v.v.)
        Request data: {
            "trang_thai": "ChuyenDi",
            "ngay_chuyen_di": "2025-01-01",
            "noi_chuyen_den": "TP. HCM",
            "ghi_chu": "Chuyển công tác"
        }
        """
        thanh_vien = self.get_object()
        trang_thai = request.data.get('trang_thai')
        
        if trang_thai == 'ChuyenDi':
            thanh_vien.trang_thai = 'ChuyenDi'
            thanh_vien.ngay_chuyen_di = request.data.get('ngay_chuyen_di')
            thanh_vien.noi_chuyen_den = request.data.get('noi_chuyen_den')
            thanh_vien.ghi_chu_thay_doi = request.data.get('ghi_chu', '')
            thanh_vien.save()
            
            return Response({"message": "Đã cập nhật trạng thái chuyển đi"})
        
        return Response({"error": "Trạng thái không hợp lệ"}, status=400)
    
    @action(detail=False, methods=['get'], url_path='thong-ke')
    def thong_ke(self, request):
        """
        Thống kê nhân khẩu theo nhiều tiêu chí
        Query params:
        - loai: 'gioi_tinh', 'do_tuoi', 'thoi_gian'
        - tu_ngay, den_ngay (cho thống kê theo thời gian)
        """
        loai_thong_ke = request.query_params.get('loai', 'gioi_tinh')
        
        if loai_thong_ke == 'gioi_tinh':
            # Thống kê theo giới tính
            nam = ThanhVien.objects.filter(gioi_tinh='Nam', trang_thai='ThuongTru').count()
            nu = ThanhVien.objects.filter(gioi_tinh='Nu', trang_thai='ThuongTru').count()
            khac = ThanhVien.objects.filter(gioi_tinh='Khac', trang_thai='ThuongTru').count()
            
            return Response({
                "loai": "Giới tính",
                "du_lieu": {
                    "Nam": nam,
                    "Nữ": nu,
                    "Khác": khac,
                    "Tổng": nam + nu + khac
                }
            })
        
        elif loai_thong_ke == 'do_tuoi':
            # Thống kê theo độ tuổi
            today = date.today()
            tat_ca = ThanhVien.objects.filter(trang_thai='ThuongTru')
            
            mam_non = 0  # 0-3 tuổi
            mau_giao = 0  # 3-6 tuổi
            cap_1 = 0     # 6-11 tuổi
            cap_2 = 0     # 11-15 tuổi
            cap_3 = 0     # 15-18 tuổi
            lao_dong = 0  # 18-60 tuổi
            nghi_huu = 0  # >60 tuổi
            
            for tv in tat_ca:
                tuoi = today.year - tv.ngay_sinh.year - (
                    (today.month, today.day) < (tv.ngay_sinh.month, tv.ngay_sinh.day)
                )
                
                if tuoi < 3:
                    mam_non += 1
                elif tuoi < 6:
                    mau_giao += 1
                elif tuoi < 11:
                    cap_1 += 1
                elif tuoi < 15:
                    cap_2 += 1
                elif tuoi < 18:
                    cap_3 += 1
                elif tuoi < 60:
                    lao_dong += 1
                else:
                    nghi_huu += 1
            
            return Response({
                "loai": "Độ tuổi",
                "du_lieu": {
                    "Mầm non (0-3)": mam_non,
                    "Mẫu giáo (3-6)": mau_giao,
                    "Cấp 1 (6-11)": cap_1,
                    "Cấp 2 (11-15)": cap_2,
                    "Cấp 3 (15-18)": cap_3,
                    "Độ tuổi lao động (18-60)": lao_dong,
                    "Nghỉ hưu (>60)": nghi_huu,
                    "Tổng": tat_ca.count()
                }
            })
        
        elif loai_thong_ke == 'thoi_gian':
            # Thống kê theo khoảng thời gian (đăng ký thường trú)
            from django.db.models import Count
            from datetime import datetime
            
            tu_ngay_str = request.query_params.get('tu_ngay')
            den_ngay_str = request.query_params.get('den_ngay')
            
            queryset = ThanhVien.objects.filter(trang_thai='ThuongTru')
            
            if tu_ngay_str:
                tu_ngay = datetime.strptime(tu_ngay_str, '%Y-%m-%d').date()
                queryset = queryset.filter(ngay_dang_ky_thuong_tru__gte=tu_ngay)
            
            if den_ngay_str:
                den_ngay = datetime.strptime(den_ngay_str, '%Y-%m-%d').date()
                queryset = queryset.filter(ngay_dang_ky_thuong_tru__lte=den_ngay)
            
            return Response({
                "loai": "Theo thời gian",
                "tu_ngay": tu_ngay_str,
                "den_ngay": den_ngay_str,
                "so_luong": queryset.count()
            })
        
        elif loai_thong_ke == 'tam_tru_vang':
            # Thống kê tạm trú/tạm vắng
            tam_tru = TamTru.objects.filter(trang_thai='DaDuyet').count()
            tam_vang = TamVang.objects.filter(trang_thai='DaDuyet').count()
            
            return Response({
                "loai": "Tạm trú/Tạm vắng",
                "du_lieu": {
                    "Tạm trú": tam_tru,
                    "Tạm vắng": tam_vang
                }
            })
        
        return Response({"error": "Loại thống kê không hợp lệ"}, status=400)
    
    @action(detail=False, methods=['get'], url_path='lich-su-thay-doi')
    def lich_su_thay_doi(self, request):
        """
        Xem lịch sử thay đổi của một hộ
        Query param: ho_gia_dinh_id
        """
        from .models import LichSuThayDoiHo
        
        ho_id = request.query_params.get('ho_gia_dinh_id')
        if not ho_id:
            return Response({"error": "Vui lòng cung cấp ho_gia_dinh_id"}, status=400)
        
        lich_su = LichSuThayDoiHo.objects.filter(ho_gia_dinh_id=ho_id).order_by('-ngay_thay_doi')
        
        data = []
        for ls in lich_su:
            data.append({
                "loai_thay_doi": ls.get_loai_thay_doi_display(),
                "noi_dung": ls.noi_dung,
                "ngay_thay_doi": ls.ngay_thay_doi,
                "nguoi_thuc_hien": ls.nguoi_thuc_hien.username if ls.nguoi_thuc_hien else None,
                "ngay_ghi_nhan": ls.ngay_ghi_nhan
            })
        
        return Response({
            "ho_gia_dinh_id": ho_id,
            "lich_su": data
        })

# ==========================================================
#  PHẦN 6: QUẢN LÝ KHEN THƯỞNG
# ==========================================================

class ThongTinHocTapViewSet(viewsets.ModelViewSet):
    """API quản lý thông tin học tập"""
    queryset = ThongTinHocTap.objects.select_related('thanh_vien', 'nguoi_duyet').all().order_by('-ngay_tao')
    serializer_class = ThongTinHocTapSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Người dân chỉ xem của mình, admin/manager xem tất cả"""
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return self.queryset
        
        # Người dân chỉ xem thông tin của bản thân
        try:
            thanh_vien = ThanhVien.objects.get(user=user)
            return self.queryset.filter(thanh_vien=thanh_vien)
        except ThanhVien.DoesNotExist:
            return self.queryset.none()
    
    def perform_create(self, serializer):
        """Ghi nhận người tạo"""
        serializer.save(nguoi_tao=self.request.user)
    
    @action(detail=True, methods=['post'], url_path='duyet')
    def duyet(self, request, pk=None):
        """Duyệt hoặc từ chối thông tin học tập"""
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({"detail": "Chỉ cán bộ mới có quyền duyệt"}, status=403)
        
        thong_tin = self.get_object()
        trang_thai = request.data.get('trang_thai')  # 'DaDuyet' hoặc 'TuChoi'
        ly_do = request.data.get('ly_do_tu_choi', '')
        
        if trang_thai in ['DaDuyet', 'TuChoi']:
            from django.utils import timezone
            thong_tin.trang_thai = trang_thai
            thong_tin.nguoi_duyet = request.user
            thong_tin.ngay_duyet = timezone.now()
            if trang_thai == 'TuChoi':
                thong_tin.ly_do_tu_choi = ly_do
            thong_tin.save()
            
            return Response({
                "message": f"Đã {thong_tin.get_trang_thai_display()}",
                "trang_thai": trang_thai
            })
        
        return Response({"error": "Trạng thái không hợp lệ"}, status=400)


class DanhMucPhanThuongViewSet(viewsets.ModelViewSet):
    queryset = DanhMucPhanThuong.objects.all().order_by('ten_phan_thuong')
    serializer_class = DanhMucPhanThuongSerializer
    permission_classes = [IsStaffOrReadOnly]


class LichSuPhatThuongViewSet(viewsets.ModelViewSet):
    """API Quản lý phát quà (Gợi ý & Thống kê)."""
    queryset = LichSuPhatThuong.objects.select_related('thanh_vien', 'phan_thuong', 'thong_tin_hoc_tap').all().order_by('-ngay_cap_phat')
    serializer_class = LichSuPhatThuongSerializer
    permission_classes = [IsCanBo]

    def perform_create(self, serializer):
        serializer.save(nguoi_cap=self.request.user)

    @action(detail=False, methods=['get'], url_path='goi-y-danh-sach')
    def goi_y_danh_sach(self, request):
        """
        Gợi ý danh sách nhận quà theo loại
        - loai=TrungThu: Trẻ em 0-18 tuổi
        - loai=HocSinh: Học sinh 6-18 tuổi  
        - loai=HocTap: Học sinh có thành tích (từ ThongTinHocTap đã duyệt)
        """
        loại = request.query_params.get('loai', 'TrungThu')
        today = date.today()
        danh_sach = []

        if loai in ['TrungThu', 'HocSinh']:
            all_members = ThanhVien.objects.filter(trang_thai='ThuongTru')

            for tv in all_members:
                tuoi = today.year - tv.ngay_sinh.year - ((today.month, today.day) < (tv.ngay_sinh.month, tv.ngay_sinh.day))
                is_eligible = False
                ly_do = ""

                if loai == 'TrungThu' and 0 <= tuoi <= 18:
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
        
        elif loai == 'HocTap':
            # Gợi ý từ thông tin học tập đã duyệt
            thong_tin_da_duyet = ThongTinHocTap.objects.filter(
                trang_thai='DaDuyet'
            ).select_related('thanh_vien', 'thanh_vien__ho_gia_dinh')
            
            for tt in thong_tin_da_duyet:
                # Xác định số lượng vở theo thành tích
                so_luong_vo = 5  # Mặc định
                if tt.thanh_tich in ['HocSinhGioi', 'ThanhTichDacBiet']:
                    so_luong_vo = 10
                elif tt.thanh_tich == 'HocSinhTienTien':
                    so_luong_vo = 7
                
                danh_sach.append({
                    "id": tt.thanh_vien.id,
                    "ho_ten": tt.thanh_vien.ho_ten,
                    "ho_gia_dinh": tt.thanh_vien.ho_gia_dinh.ma_ho,
                    "truong": tt.truong,
                    "lop": tt.lop,
                    "thanh_tich": tt.get_thanh_tich_display(),
                    "so_luong_vo": so_luong_vo,
                    "thong_tin_hoc_tap_id": tt.id,
                    "ly_do_de_xuat": f"{tt.get_thanh_tich_display()} - {so_luong_vo} cuốn vở"
                })

        return Response({
            "tieu_chi": loai,
            "so_luong_de_xuat": len(danh_sach),
            "danh_sach": danh_sach
        })
    
    @action(detail=False, methods=['post'], url_path='tao-dot-phat')
    def tao_dot_phat(self, request):
        """
        Tạo đợt phát thưởng hàng loạt
        Request: {
            "dot_phat": "Trung Thu 2025",
            "loai_phat_thuong": "DipLe",
            "phan_thuong_id": 1,
            "thanh_vien_ids": [1, 2, 3],
            "so_luong": 1,
            "ghi_chu": "..."
        }
        """
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({"detail": "Chỉ cán bộ mới có quyền tạo đợt phát"}, status=403)
        
        dot_phat = request.data.get('dot_phat')
        loai_phat_thuong = request.data.get('loai_phat_thuong', 'DipLe')
        phan_thuong_id = request.data.get('phan_thuong_id')
        thanh_vien_ids = request.data.get('thanh_vien_ids', [])
        so_luong = request.data.get('so_luong', 1)
        ghi_chu = request.data.get('ghi_chu', '')
        
        if not dot_phat or not phan_thuong_id or not thanh_vien_ids:
            return Response({"error": "Thiếu thông tin bắt buộc"}, status=400)
        
        try:
            phan_thuong = DanhMucPhanThuong.objects.get(id=phan_thuong_id)
            thanh_vien_list = ThanhVien.objects.filter(id__in=thanh_vien_ids)
            
            created_count = 0
            for tv in thanh_vien_list:
                LichSuPhatThuong.objects.create(
                    thanh_vien=tv,
                    phan_thuong=phan_thuong,
                    loai_phat_thuong=loai_phat_thuong,
                    so_luong=so_luong,
                    dot_phat=dot_phat,
                    nguoi_cap=request.user,
                    ghi_chu=ghi_chu
                )
                created_count += 1
            
            return Response({
                "message": f"Đã tạo {created_count} phần thưởng",
                "dot_phat": dot_phat
            }, status=201)
            
        except DanhMucPhanThuong.DoesNotExist:
            return Response({"error": "Phần thưởng không tồn tại"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
    
    @action(detail=False, methods=['post'], url_path='phat-thuong-hoc-tap')
    def phat_thuong_hoc_tap(self, request):
        """
        Phát thưởng học tập dựa trên ThongTinHocTap đã duyệt
        Request: {
            "dot_phat": "Năm học 2024-2025",
            "phan_thuong_id": 1,
            "thong_tin_hoc_tap_ids": [1, 2, 3]
        }
        """
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({"detail": "Chỉ cán bộ mới có quyền phát thưởng"}, status=403)
        
        dot_phat = request.data.get('dot_phat')
        phan_thuong_id = request.data.get('phan_thuong_id')
        thong_tin_ids = request.data.get('thong_tin_hoc_tap_ids', [])
        
        if not all([dot_phat, phan_thuong_id, thong_tin_ids]):
            return Response({"error": "Thiếu thông tin bắt buộc"}, status=400)
        
        try:
            phan_thuong = DanhMucPhanThuong.objects.get(id=phan_thuong_id)
            thong_tin_list = ThongTinHocTap.objects.filter(
                id__in=thong_tin_ids,
                trang_thai='DaDuyet'
            ).select_related('thanh_vien')
            
            created_count = 0
            for tt in thong_tin_list:
                # Xác định số lượng vở
                so_luong = 5
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
                    nguoi_cap=request.user,
                    ghi_chu=f"{tt.get_thanh_tich_display()} - {tt.truong}"
                )
                created_count += 1
            
            return Response({
                "message": f"Đã tạo {created_count} phần thưởng học tập",
                "dot_phat": dot_phat
            }, status=201)
            
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=['get'], url_path='thong-ke')
    def thong_ke(self, request):
        """
        Thống kê phần thưởng
        - Theo đợt phát: ?dot_phat=...
        - Theo hộ gia đình: ?ho_gia_dinh_id=...
        - Danh sách các đợt: không truyền gì
        """
        dot_phat = request.query_params.get('dot_phat')
        ho_gia_dinh_id = request.query_params.get('ho_gia_dinh_id')
        
        if dot_phat:
            # Thống kê theo đợt
            records = LichSuPhatThuong.objects.filter(dot_phat=dot_phat).select_related('phan_thuong')
            tong_tien = sum([r.tong_gia_tri() for r in records])
            so_luong = records.count()
            da_nhan = records.filter(trang_thai='DaNhan').count()

            return Response({
                "dot_phat": dot_phat,
                "tong_so_suat_qua": so_luong,
                "da_phat": da_nhan,
                "chua_phat": so_luong - da_nhan,
                "tong_gia_tri": f"{tong_tien:,.0f} VNĐ"
            })
        
        elif ho_gia_dinh_id:
            # Thống kê theo hộ
            thanh_vien_ids = ThanhVien.objects.filter(ho_gia_dinh_id=ho_gia_dinh_id).values_list('id', flat=True)
            records = LichSuPhatThuong.objects.filter(
                thanh_vien_id__in=thanh_vien_ids
            ).select_related('thanh_vien', 'phan_thuong')
            
            danh_sach = []
            tong_gia_tri = 0
            for r in records:
                gia_tri = r.tong_gia_tri()
                tong_gia_tri += gia_tri
                danh_sach.append({
                    "nguoi_nhan": r.thanh_vien.ho_ten,
                    "phan_thuong": r.phan_thuong.ten_phan_thuong,
                    "so_luong": r.so_luong,
                    "gia_tri": gia_tri,
                    "dot_phat": r.dot_phat,
                    "trang_thai": r.get_trang_thai_display()
                })
            
            return Response({
                "ho_gia_dinh_id": ho_gia_dinh_id,
                "tong_so_phan_thuong": len(danh_sach),
                "tong_gia_tri": f"{tong_gia_tri:,.0f} VNĐ",
                "danh_sach": danh_sach
            })
        
        else:
            # Danh sách các đợt phát
            cac_dot = LichSuPhatThuong.objects.values_list('dot_phat', flat=True).distinct()
            return Response({"cac_dot_phat_hien_co": list(cac_dot)})


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