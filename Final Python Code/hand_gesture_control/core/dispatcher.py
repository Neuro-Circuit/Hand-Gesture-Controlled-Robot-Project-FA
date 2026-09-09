import time
from typing import Callable, Dict, List, Set

from .command import Command
from .landmarks import to_points
from .gesture_base import GestureDetector
from .two_hand_base import TwoHandDetector


class GestureManager:
    """
    اجرای تشخیص‌گرهای تک‌دست و دودست روی هر فریم و پخش دستورات خروجی به سینک‌ها.

    نکته مهم درباره پشتیبانی از دو دست: هر تشخیص‌گر تک‌دست (مثل HandMovementDetector)
    حافظه داخلی دارد (تاریخچه حرکت، وضعیت قبلی و ...). اگر یک نمونه مشترک بین هر دو
    دست استفاده شود، تاریخچه دو دست با هم قاطی می‌شود و تشخیص اشتباه می‌شود. به همین
    دلیل GestureManager به‌جای گرفتن یک لیست ثابت از تشخیص‌گرها، یک «کارخانه»
    (detector_factory) می‌گیرد و برای هر برچسب دست ('Left'/'Right') اولین بار که دیده
    می‌شود، یک مجموعه کاملاً تازه و مستقل از تشخیص‌گرها می‌سازد.
    """

    def __init__(self,
                 detector_factory: Callable[[], List[GestureDetector]],
                 two_hand_detectors: List[TwoHandDetector],
                 sinks: list):
        self.detector_factory = detector_factory
        self.two_hand_detectors = two_hand_detectors
        self.sinks = sinks
        self._detectors_by_hand: Dict[str, List[GestureDetector]] = {}

    def _get_hand_detectors(self, hand_label: str) -> List[GestureDetector]:
        if hand_label not in self._detectors_by_hand:
            self._detectors_by_hand[hand_label] = self.detector_factory()
        return self._detectors_by_hand[hand_label]

    def process_hand(self, hand_landmarks, frame_shape, hand_label: str) -> List[Command]:
        points = to_points(hand_landmarks)
        timestamp = time.time()
        detectors = self._get_hand_detectors(hand_label)

        commands: List[Command] = []
        for detector in detectors:
            try:
                commands.extend(detector.update(points, frame_shape, timestamp, hand_label))
            except Exception as e:
                print(f"[GestureManager] خطا در تشخیص‌گر '{detector.name}' (دست {hand_label}): {e}")

        for cmd in commands:
            self._emit(cmd)
        return commands

    def process_pair(self, left_hand_landmarks, right_hand_landmarks, frame_shape) -> List[Command]:
        """فقط زمانی فراخوانی شود که هر دو دست ('Left' و 'Right') در همین فریم دیده شده باشند."""
        left_points = to_points(left_hand_landmarks)
        right_points = to_points(right_hand_landmarks)
        timestamp = time.time()

        commands: List[Command] = []
        for detector in self.two_hand_detectors:
            try:
                commands.extend(detector.update(left_points, right_points, frame_shape, timestamp))
            except Exception as e:
                print(f"[GestureManager] خطا در تشخیص‌گر دودست '{detector.name}': {e}")

        for cmd in commands:
            self._emit(cmd)
        return commands

    def reset_pair(self):
        """وقتی دیگر هر دو دست هم‌زمان دیده نمی‌شوند، حالت داخلی تشخیص‌گرهای دودست ریست می‌شود."""
        for detector in self.two_hand_detectors:
            detector.reset()

    def end_frame(self, seen_hand_labels: Set[str]):
        """
        در پایان هر فریم (چه صفر دست دیده شده باشد چه یک یا دو دست) فراخوانی می‌شود؛
        حالت داخلی هر دستی که در همین فریم دیده نشده را ریست می‌کند - مثلاً اگر دست
        راست از فریم خارج شود ولی دست چپ بماند، فقط تشخیص‌گرهای دست راست ریست می‌شوند.
        """
        for label, detectors in self._detectors_by_hand.items():
            if label not in seen_hand_labels:
                for d in detectors:
                    d.reset()

    def _emit(self, command: Command):
        for sink in self.sinks:
            if not sink.should_emit(command):
                continue
            try:
                sink.emit(command)
            except Exception as e:
                print(f"[GestureManager] خطا در سینک '{sink.__class__.__name__}': {e}")

    def close(self):
        for sink in self.sinks:
            sink.close()
