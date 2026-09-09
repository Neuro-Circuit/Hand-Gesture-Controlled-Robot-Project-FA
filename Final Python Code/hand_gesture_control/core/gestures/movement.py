from collections import deque
from typing import List
from ..gesture_base import GestureDetector
from ..command import Command, CommandRegistry
from ..landmarks import palm_center, hand_size

CommandRegistry.register("hand.move.left", 6, "حرکت دست به چپ", "Hand Move Left", "movement",
                          "مرکز کف دست به سمت چپ جابه‌جا می‌شود", {"speed": "float"})
CommandRegistry.register("hand.move.right", 7, "حرکت دست به راست", "Hand Move Right", "movement",
                          "مرکز کف دست به سمت راست جابه‌جا می‌شود", {"speed": "float"})
CommandRegistry.register("hand.move.up", 8, "حرکت دست به بالا", "Hand Move Up", "movement",
                          "مرکز کف دست به سمت بالا جابه‌جا می‌شود", {"speed": "float"})
CommandRegistry.register("hand.move.down", 9, "حرکت دست به پایین", "Hand Move Down", "movement",
                          "مرکز کف دست به سمت پایین جابه‌جا می‌شود", {"speed": "float"})
CommandRegistry.register("hand.move.forward", 10, "حرکت دست به جلو", "Hand Move Forward", "movement",
                          "دست به دوربین نزدیک می‌شود (بر اساس بزرگ‌تر شدن اندازه دست)", {"speed": "float"})
CommandRegistry.register("hand.move.backward", 11, "حرکت دست به عقب", "Hand Move Backward", "movement",
                          "دست از دوربین دور می‌شود (بر اساس کوچک‌تر شدن اندازه دست)", {"speed": "float"})


class HandMovementDetector(GestureDetector):
    """
    جابه‌جایی کلی دست (صرف‌نظر از حالت انگشتان) را در ۶ جهت تشخیص می‌دهد.
    جلو/عقب به دلیل نبود سنسور عمق واقعی، از روی تغییر اندازه ظاهری دست تخمین زده می‌شود.
    """
    name = "hand_movement"

    def __init__(self, config: dict):
        super().__init__(config)
        cfg = config.get("movement", {})
        self.history_len = cfg.get("history_len", 6)
        self.move_th = cfg.get("move_threshold", 0.035)
        self.depth_th = cfg.get("depth_threshold", 0.06)
        self.cooldown = cfg.get("cooldown", 0.35)
        self._pos_hist = deque(maxlen=self.history_len)
        self._size_hist = deque(maxlen=self.history_len)
        self._last_emit = 0.0

    def reset(self):
        self._pos_hist.clear()
        self._size_hist.clear()

    def update(self, points, frame_shape, timestamp, hand_label) -> List[Command]:
        center = palm_center(points)
        size = hand_size(points)
        self._pos_hist.append(center)
        self._size_hist.append(size)

        if len(self._pos_hist) < self.history_len:
            return []
        if timestamp - self._last_emit < self.cooldown:
            return []

        dx = self._pos_hist[-1][0] - self._pos_hist[0][0]
        dy = self._pos_hist[-1][1] - self._pos_hist[0][1]
        dsize = self._size_hist[-1] - self._size_hist[0]

        commands = []
        if abs(dsize) > self.depth_th:
            cid = "hand.move.forward" if dsize > 0 else "hand.move.backward"
            commands.append(CommandRegistry.make_command(
                cid, params={"speed": round(abs(dsize), 4)}, hand=hand_label))
        elif abs(dx) > abs(dy) and abs(dx) > self.move_th:
            cid = "hand.move.right" if dx > 0 else "hand.move.left"
            commands.append(CommandRegistry.make_command(
                cid, params={"speed": round(abs(dx), 4)}, hand=hand_label))
        elif abs(dy) > self.move_th:
            cid = "hand.move.down" if dy > 0 else "hand.move.up"
            commands.append(CommandRegistry.make_command(
                cid, params={"speed": round(abs(dy), 4)}, hand=hand_label))

        if commands:
            self._last_emit = timestamp
            self._pos_hist.clear()
            self._size_hist.clear()
        return commands
