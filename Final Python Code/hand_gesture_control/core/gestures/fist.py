from typing import List
from ..gesture_base import GestureDetector
from ..command import Command, CommandRegistry
from ..landmarks import finger_states

CommandRegistry.register("hand.fist", 4, "مشت کردن دست", "Fist", "gesture",
                          "چهار انگشت اشاره تا کوچک کاملاً جمع می‌شوند", {})
CommandRegistry.register("hand.open", 5, "باز کردن دست", "Open Hand", "gesture",
                          "دست از حالت مشت خارج و باز می‌شود", {})


class FistDetector(GestureDetector):
    name = "fist"

    def __init__(self, config):
        super().__init__(config)
        self.threshold = config.get("fist", {}).get("curl_angle_threshold", 90) + 50
        self._is_fist = False

    def reset(self):
        self._is_fist = False

    def update(self, points, frame_shape, timestamp, hand_label) -> List[Command]:
        states = finger_states(points, threshold=self.threshold)
        currently_fist = all(not states[f] for f in ("index", "middle", "ring", "pinky"))

        commands = []
        if currently_fist and not self._is_fist:
            commands.append(CommandRegistry.make_command("hand.fist", hand=hand_label))
        elif not currently_fist and self._is_fist:
            commands.append(CommandRegistry.make_command("hand.open", hand=hand_label))
        self._is_fist = currently_fist
        return commands
