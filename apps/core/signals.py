from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from apps.users.models import UserProfile

# ==========================================================
#  SIGNALS: TỰ ĐỘNG HÓA QUY TRÌNH
# ==========================================================
# LƯU Ý: Signal tạo UserProfile đã được định nghĩa trong apps/users/models.py
# File này giữ lại để có thể thêm các signal khác nếu cần trong tương lai

# @receiver(post_save, sender=User)
# def create_profile(sender, instance, created, **kwargs):
#     """
#     Signal này đã được chuyển sang apps/users/models.py
#     để tránh duplicate và tập trung quản lý authentication ở một nơi
#     """
#     pass
