from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

# ==========================================================
#  SIGNALS: TỰ ĐỘNG HÓA QUY TRÌNH
# ==========================================================

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Trigger: Chạy ngay sau khi một User mới được lưu vào database.
    Mục đích: Tự động tạo 'Hồ sơ người dùng' (UserProfile) đi kèm.
    
    Tại sao quan trọng?
    - Django User mặc định chỉ có username/password.
    - Hệ thống của ta cần lưu thêm 'Role' (Tổ trưởng/Cán bộ/Dân).
    - Signal này đảm bảo không bao giờ có User nào bị thiếu Profile.
    """
    if created:
        # Sử dụng get_or_create thay vì create thuần túy.
        # Lý do: Trong một số trường hợp (như admin thao tác nhanh hoặc race condition),
        # signal có thể bị gọi 2 lần, gây lỗi "Duplicate entry".
        # Hàm này an toàn hơn: Nếu chưa có thì tạo, có rồi thì thôi.
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={'role': 'NGUOI_DAN'} # Mặc định vai trò là Người dân
        )