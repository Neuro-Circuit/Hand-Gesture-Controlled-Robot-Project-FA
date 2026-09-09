from abc import ABC, abstractmethod
from typing import List
from .command import Command


class TwoHandDetector(ABC):
    """
    کلاس پایه برای تشخیص‌گرهایی که به‌طور هم‌زمان به هر دو دست نیاز دارند - مثلاً
    برای ساخت یک شکل هندسی بین دو دست، یا اندازه‌گیری فاصله/زاویه بین آن‌ها.

    برخلاف GestureDetector (که فقط نقاط یک دست را می‌گیرد)، متد update اینجا نقاط
    هر دو دست را هم‌زمان دریافت می‌کند. GestureManager این تشخیص‌گرها را فقط زمانی
    فراخوانی می‌کند که هر دو دست ('Left' و 'Right') در یک فریم دیده شده باشند.

    برای افزودن یک قابلیت دودستی جدید، از همین کلاس ارث‌بری کنید (نمونه در
    core/gestures/two_hand_frame.py) و نمونه‌ای از آن را در main.py به
    build_two_hand_detectors اضافه کنید.
    """

    name: str = "two_hand_base"

    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def update(self, left_points, right_points, frame_shape, timestamp: float) -> List[Command]:
        """
        left_points / right_points: هرکدام لیست ۲۱ نقطه (x, y, z) نرمال‌شده یک دست.
        ترتیب چپ/راست بر اساس برچسب واقعی دست (handedness) تضمین می‌شود.
        """
        raise NotImplementedError

    def reset(self):
        """وقتی دیگر هر دو دست هم‌زمان دیده نمی‌شوند (یکی از دو دست از فریم خارج شد) فراخوانی می‌شود."""
        pass
