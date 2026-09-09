"""
نمونه‌ای از افزودن یک قابلیت کاملاً جدید که به هر دو دست هم‌زمان نیاز دارد -
بدون تغییر هیچ فایلی در core/. اینجا فاصله بین دو دست را اندازه می‌گیرد و وقتی
خیلی به هم نزدیک شوند (کف دو دست تقریباً روی هم) یک دستور "hands.clap" صادر می‌کند.

نحوه استفاده واقعی:
  1. این فایل را (یا محتوای مشابه) در core/gestures/ قرار دهید.
  2. در main.py، HandsClapDetector را ایمپورت و یک نمونه از آن را به لیست
     بازگشتی build_two_hand_detectors اضافه کنید.
  3. اجرا کنید - نیازی به تغییر dispatcher, hand_tracker یا main loop نیست.
"""
import os
import sys
from typing import List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.two_hand_base import TwoHandDetector
from core.command import Command, CommandRegistry
from core.landmarks import palm_center, distance_2d

# کد 21 چون کدهای 0 تا 20 در core/gestures/*.py و examples/custom_gesture_example.py
# قبلاً استفاده شده‌اند - هر کد باید یکتا باشد
CommandRegistry.register("hands.clap", 21, "به‌هم‌کوبیدن دو دست", "Hands Clap", "pair",
                          "کف دو دست تقریباً روی هم قرار می‌گیرند (فاصله بسیار کم)", {})


class HandsClapDetector(TwoHandDetector):
    name = "hands_clap"

    def __init__(self, config):
        super().__init__(config)
        self.threshold = config.get("hands_clap", {}).get("distance_threshold", 0.08)
        self._clapping = False

    def reset(self):
        self._clapping = False

    def update(self, left_points, right_points, frame_shape, timestamp) -> List[Command]:
        d = distance_2d(palm_center(left_points), palm_center(right_points))
        is_close = d < self.threshold

        commands = []
        if is_close and not self._clapping:
            commands.append(CommandRegistry.make_command("hands.clap", hand="Both"))
        self._clapping = is_close
        return commands


if __name__ == "__main__":
    print("این ماژول برای ایمپورت شدن در main.py طراحی شده، نه اجرای مستقل.")
