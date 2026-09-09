from collections import deque
from typing import List
from ..gesture_base import GestureDetector
from ..command import Command, CommandRegistry
from ..landmarks import distance_2d

CommandRegistry.register("hand.pinch.start", 12, "شروع نزدیک کردن شست و اشاره", "Pinch Start",
                          "gesture", "نوک شست و نوک اشاره به هم نزدیک می‌شوند", {})
CommandRegistry.register("hand.pinch.rub", 13, "مالیدن شست و اشاره به هم", "Pinch Rub", "gesture",
                          "دو انگشت در حالت نزدیک، حرکت رفت‌وبرگشتی (مالش) انجام می‌دهند",
                          {"intensity": "float"})
CommandRegistry.register("hand.pinch.end", 14, "پایان نزدیک کردن شست و اشاره", "Pinch End",
                          "gesture", "", {})


class PinchRubDetector(GestureDetector):
    name = "pinch_rub"

    def __init__(self, config):
        super().__init__(config)
        cfg = config.get("pinch_rub", {})
        self.pinch_dist = cfg.get("pinch_distance", 0.045)
        self.rub_path_th = cfg.get("rub_path_threshold", 0.12)
        self.window = cfg.get("window", 10)
        self._mid_hist = deque(maxlen=self.window)
        self._pinching = False

    def reset(self):
        self._mid_hist.clear()
        self._pinching = False

    def update(self, points, frame_shape, timestamp, hand_label) -> List[Command]:
        thumb_tip, index_tip = points[4], points[8]
        d = distance_2d(thumb_tip, index_tip)
        is_pinch = d < self.pinch_dist
        commands = []

        if is_pinch and not self._pinching:
            commands.append(CommandRegistry.make_command("hand.pinch.start", hand=hand_label))
            self._mid_hist.clear()

        if is_pinch:
            mid = ((thumb_tip[0] + index_tip[0]) / 2, (thumb_tip[1] + index_tip[1]) / 2)
            self._mid_hist.append(mid)
            if len(self._mid_hist) >= self.window:
                path = sum(distance_2d(self._mid_hist[i], self._mid_hist[i + 1])
                           for i in range(len(self._mid_hist) - 1))
                if path > self.rub_path_th:
                    commands.append(CommandRegistry.make_command(
                        "hand.pinch.rub", params={"intensity": round(path, 4)}, hand=hand_label))
                    self._mid_hist.clear()

        if not is_pinch and self._pinching:
            commands.append(CommandRegistry.make_command("hand.pinch.end", hand=hand_label))
            self._mid_hist.clear()

        self._pinching = is_pinch
        return commands
