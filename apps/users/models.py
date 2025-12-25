from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """
    Mở rộng User model của Django với thông tin phân quyền
    """
    ROLE_CHOICES = [
        ('admin', 'Quản trị viên'),
        ('citizenship_manager', 'Quản lý công dân'),
        ('commendation_manager', 'Quản lý khen thưởng'),
        ('citizen', 'Dân cư'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='citizen')
    cccd_id = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name='Số CCCD')
    full_name = models.CharField(max_length=100, blank=True, verbose_name='Họ và tên')
    working_unit_id = models.CharField(max_length=10, null=True, blank=True, verbose_name='Đơn vị công tác')
    is_active = models.BooleanField(default=True, verbose_name='Đang hoạt động')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'Hồ sơ người dùng'
        verbose_name_plural = 'Hồ sơ người dùng'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    def is_manager(self):
        """Kiểm tra có phải quản lý không"""
        return self.role in ['admin', 'citizenship_manager', 'commendation_manager']


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Tự động tạo profile khi tạo user mới"""
    if created:
        UserProfile.objects.create(user=instance)
