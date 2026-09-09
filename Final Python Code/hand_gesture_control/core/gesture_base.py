from abc import ABC, abstractmethod
from typing import List
from .command import Command


class GestureDetector(ABC):
    """
    کلاس پایه برای هر تشخیص‌گر حرکت.

    برای افزودن یک حرکت جدید به سیستم:
      1. یک کلاس جدید بسازید که از GestureDetector ارث‌بری می‌کند.
      2. دستور(های) خروجی آن را با CommandRegistry.register(...) ثبت کنید.
      3. متد update را پیاده‌سازی کنید.
      4. یک نمونه از کلاس را در main.py به لیست build_detectors اضافه کنید.

    هیچ نیازی به تغییر هسته برنامه (dispatcher, hand_tracker, main loop) نیست.
    نمونه کامل: examples/custom_gesture_example.py
    """

    name: str = "base"

    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def update(self, points, frame_shape, timestamp: float, hand_label: str) -> List[Command]:
        """
        points: لیست ۲۱ نقطه (x, y, z) نرمال‌شده دست، مطابق ترتیب استاندارد MediaPipe
        frame_shape: (height, width, channels) فریم فعلی دوربین
        timestamp: زمان یونیکس لحظه پردازش فریم
        hand_label: "Left" یا "Right"

        بازگشت: لیستی از Command (در بیشتر فریم‌ها می‌تواند خالی باشد)
        """
        raise NotImplementedError

    def reset(self):
        """وقتی دست از دید دوربین خارج می‌شود فراخوانی می‌شود تا حالت داخلی پاک شود."""
        pass
