from abc import ABC, abstractmethod
from typing import Iterable, Optional
from ..command import Command


class OutputSink(ABC):
    """
    رابط پایه خروجی. برای اتصال این سیستم به یک نرم‌افزار دیگر
    (رباتیک، بازی، اتوماسیون خانه هوشمند، انیمیشن سه‌بعدی و ...) کافیست یک کلاس
    جدید از این کلاس ارث‌بری کرده و متد emit را برای انتقال دستور به سیستم مقصد
    پیاده‌سازی کنید. نیازی به تغییر GestureManager یا main.py نیست.

    پارامتر categories امکان فیلتر کردن بر اساس دسته دستور را می‌دهد؛ مثلاً
    می‌توان کنسول را فقط برای دسته "gesture"/"movement" فعال کرد و فریم‌های
    پرحجم "rig" را فقط به لاگ/وب‌سوکت فرستاد.
    """

    def __init__(self, categories: Optional[Iterable[str]] = None):
        self.categories = set(categories) if categories else None

    def should_emit(self, command: Command) -> bool:
        return self.categories is None or command.category in self.categories

    @abstractmethod
    def emit(self, command: Command):
        raise NotImplementedError

    def close(self):
        pass
