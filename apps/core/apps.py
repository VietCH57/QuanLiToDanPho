from django.apps import AppConfig

class CoreConfig(AppConfig):
    """
    Class cấu hình cho ứng dụng 'Core'.
    Nhiệm vụ quan trọng nhất: Kích hoạt Signals khi ứng dụng khởi động.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = "Quản Lý Tổ Dân Phố"

    def ready(self):
        """
        Hàm này chạy 1 lần duy nhất khi Server khởi động.
        Ta import signals ở đây để Django biết mà lắng nghe sự kiện (như tạo User).
        """
        import apps.core.signals