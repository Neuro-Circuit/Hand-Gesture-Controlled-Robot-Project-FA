from typing import List
from ..gesture_base import GestureDetector
from ..command import Command, CommandRegistry
from ..landmarks import finger_states

CommandRegistry.register("hand.thumb.show", 15, "نشان دادن انگشت شست", "Thumb Shown", "gesture",
                          "فقط انگشت شست کشیده و چهار انگشت دیگر جمع هستند", {"direction": "str"})
CommandRegistry.register("hand.thumb.hide", 16, "پنهان شدن انگشت شست", "Thumb Hidden", "gesture", "", {})


class ThumbDetector(GestureDetector):
    name = "thumbs"

    def __init__(self, config):
        super().__init__(config)
        self.threshold = config.get("thumbs", {}).get("curl_angle_threshold", 90) + 50
        self._shown = False

    def reset(self):
        self._shown = False

    def update(self, points, frame_shape, timestamp, hand_label) -> List[Command]:
        states = finger_states(points, threshold=self.threshold)
        thumb_only = states["thumb"] and not any(
            states[f] for f in ("index", "middle", "ring", "pinky"))

        commands = []
        if thumb_only and not self._shown:
            wrist_x, wrist_y = points[0][0], points[0][1]
            tip_x, tip_y = points[4][0], points[4][1]
            if abs(tip_y - wrist_y) > abs(tip_x - wrist_x):
                direction = "up" if tip_y < wrist_y else "down"
            else:
                direction = "right" if tip_x > wrist_x else "left"
            commands.append(CommandRegistry.make_command(
                "hand.thumb.show", params={"direction": direction}, hand=hand_label))
        elif not thumb_only and self._shown:
            commands.append(CommandRegistry.make_command("hand.thumb.hide", hand=hand_label))
        self._shown = thumb_only
        return commands
