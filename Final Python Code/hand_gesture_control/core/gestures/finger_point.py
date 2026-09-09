from collections import deque
from typing import List
from ..gesture_base import GestureDetector
from ..command import Command, CommandRegistry
from ..landmarks import finger_states

CommandRegistry.register("finger.swipe.down", 0, "حرکت انگشت اشاره به پایین", "Finger Swipe Down",
                          "gesture", "در حالت اشاره‌کردن، نوک انگشت اشاره به پایین حرکت می‌کند",
                          {"speed": "float"})
CommandRegistry.register("finger.swipe.up", 1, "حرکت انگشت اشاره به بالا", "Finger Swipe Up",
                          "gesture", "در حالت اشاره‌کردن، نوک انگشت اشاره به بالا حرکت می‌کند",
                          {"speed": "float"})
CommandRegistry.register("finger.swipe.left", 2, "حرکت انگشت اشاره به چپ", "Finger Swipe Left",
                          "gesture", "در حالت اشاره‌کردن، نوک انگشت اشاره به چپ حرکت می‌کند",
                          {"speed": "float"})
CommandRegistry.register("finger.swipe.right", 3, "حرکت انگشت اشاره به راست", "Finger Swipe Right",
                          "gesture", "در حالت اشاره‌کردن، نوک انگشت اشاره به راست حرکت می‌کند",
                          {"speed": "float"})


class FingerPointSwipeDetector(GestureDetector):
    """فقط زمانی فعال می‌شود که تنها انگشت اشاره کشیده باشد (حالت 'اشاره کردن')."""
    name = "finger_point_swipe"

    def __init__(self, config):
        super().__init__(config)
        cfg = config.get("finger_swipe", {})
        self.history_len = cfg.get("history_len", 6)
        self.threshold = cfg.get("swipe_threshold", 0.05)
        self.cooldown = cfg.get("cooldown", 0.3)
        self._hist = deque(maxlen=self.history_len)
        self._last_emit = 0.0

    def reset(self):
        self._hist.clear()

    def update(self, points, frame_shape, timestamp, hand_label) -> List[Command]:
        states = finger_states(points)
        pointing = states["index"] and not states["middle"] and not states["ring"] and not states["pinky"]

        if not pointing:
            self._hist.clear()
            return []

        self._hist.append(points[8])  # نوک انگشت اشاره
        if len(self._hist) < self.history_len or timestamp - self._last_emit < self.cooldown:
            return []

        dx = self._hist[-1][0] - self._hist[0][0]
        dy = self._hist[-1][1] - self._hist[0][1]
        commands = []

        if abs(dx) > abs(dy) and abs(dx) > self.threshold:
            cid = "finger.swipe.right" if dx > 0 else "finger.swipe.left"
            commands.append(CommandRegistry.make_command(
                cid, params={"speed": round(abs(dx), 4)}, hand=hand_label))
        elif abs(dy) > self.threshold:
            cid = "finger.swipe.down" if dy > 0 else "finger.swipe.up"
            commands.append(CommandRegistry.make_command(
                cid, params={"speed": round(abs(dy), 4)}, hand=hand_label))

        if commands:
            self._last_emit = timestamp
            self._hist.clear()
        return commands
