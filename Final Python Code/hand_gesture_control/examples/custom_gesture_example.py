"""
نمونه‌ای از افزودن یک حرکت کاملاً جدید به سیستم، بدون تغییر هیچ فایلی در core/.
اینجا یک تشخیص‌گر برای علامت "صلح" (V - انگشتان اشاره و میانی باز) اضافه می‌شود.

نحوه استفاده واقعی:
  1. این فایل را (یا محتوای مشابه) در core/gestures/ قرار دهید.
  2. در main.py، PeaceSignDetector را ایمپورت و یک نمونه از آن را
     به لیست بازگشتی build_detectors اضافه کنید.
  3. اجرا کنید - نیازی به تغییر dispatcher, hand_tracker یا main loop نیست.
"""
import os
import sys
from typing import List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.gesture_base import GestureDetector
from core.command import Command, CommandRegistry
from core.landmarks import finger_states

CommandRegistry.register("hand.peace_sign", 20, "علامت صلح (V)", "Peace Sign", "gesture",
                          "انگشتان اشاره و میانی باز و بقیه انگشتان جمع هستند", {})


class PeaceSignDetector(GestureDetector):
    name = "peace_sign"

    def __init__(self, config):
        super().__init__(config)
        self._shown = False

    def reset(self):
        self._shown = False

    def update(self, points, frame_shape, timestamp, hand_label) -> List[Command]:
        states = finger_states(points)
        is_peace = states["index"] and states["middle"] and not states["ring"] and not states["pinky"]

        commands = []
        if is_peace and not self._shown:
            commands.append(CommandRegistry.make_command("hand.peace_sign", hand=hand_label))
        self._shown = is_peace
        return commands


if __name__ == "__main__":
    print("این ماژول برای ایمپورت شدن در main.py طراحی شده، نه اجرای مستقل.")
