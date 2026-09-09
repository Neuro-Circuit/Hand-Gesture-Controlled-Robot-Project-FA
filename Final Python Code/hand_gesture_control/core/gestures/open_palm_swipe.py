from collections import deque
from typing import List
from ..gesture_base import GestureDetector
from ..command import Command, CommandRegistry
from ..landmarks import finger_states, palm_center

CommandRegistry.register("hand.open_palm.swipe_right", 17, "حرکت دست باز به راست",
                          "Open Palm Swipe Right", "gesture",
                          "تمام پنج انگشت باز هستند و کل دست به سمت راست حرکت می‌کند",
                          {"speed": "float"})


class OpenPalmSwipeDetector(GestureDetector):
    name = "open_palm_swipe"

    def __init__(self, config):
        super().__init__(config)
        cfg = config.get("open_palm_swipe", {})
        self.history_len = cfg.get("history_len", 6)
        self.threshold = cfg.get("move_threshold", 0.05)
        self.cooldown = cfg.get("cooldown", 0.35)
        self._hist = deque(maxlen=self.history_len)
        self._last_emit = 0.0

    def reset(self):
        self._hist.clear()

    def update(self, points, frame_shape, timestamp, hand_label) -> List[Command]:
        states = finger_states(points)
        is_open = all(states.values())

        if not is_open:
            self._hist.clear()
            return []

        self._hist.append(palm_center(points))
        if len(self._hist) < self.history_len or timestamp - self._last_emit < self.cooldown:
            return []

        dx = self._hist[-1][0] - self._hist[0][0]
        commands = []
        if dx > self.threshold:
            commands.append(CommandRegistry.make_command(
                "hand.open_palm.swipe_right", params={"speed": round(dx, 4)}, hand=hand_label))
            self._last_emit = timestamp
            self._hist.clear()
        return commands
