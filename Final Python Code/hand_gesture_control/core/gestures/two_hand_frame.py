from typing import List
from ..two_hand_base import TwoHandDetector
from ..command import Command, CommandRegistry
from ..two_hand_geometry import compute_pair_quad

CommandRegistry.register(
    "hands.pair.frame", 19, "شکل هندسی بین دو دست", "Two-Hand Frame Shape", "pair",
    "وقتی هر دو دست هم‌زمان دیده شوند، یک چهارضلعی بین نقاط مرجع دو دست (مچ و قاعده "
    "انگشت اشاره) ساخته می‌شود که با حرکت دست‌ها تغییر شکل/اندازه/زاویه می‌دهد - دقیقاً "
    "همان الگوی 'قاب‌گیری با دو دست' که در دموهای MediaPipe دیده می‌شود.",
    {
        "corners": "چهار نقطه گوشه به ترتیب [پایین‌چپ, بالاچپ, بالاراست, پایین‌راست]، هرکدام [x, y]",
        "width": "فاصله نرمال‌شده بین مچ دو دست (مثلاً برای کنترل زوم قابل استفاده است)",
        "height": "میانگین فاصله مچ تا قاعده انگشت اشاره هر دست",
        "center": "[x, y] مرکز چهارضلعی",
        "angle_deg": "زاویه شیب خط اتصال دو دست بر حسب درجه",
        "area": "مساحت تقریبی چهارضلعی (نرمال‌شده، بین 0 و 1)",
    },
)


class TwoHandFrameDetector(TwoHandDetector):
    """
    فقط وقتی هر دو دست هم‌زمان دیده شوند فعال می‌شود. با نرخ قابل‌تنظیم (مثل hand_rig)
    داده هندسی چهارضلعی بین دو دست را صادر می‌کند - هم برای مصرف توسط سیستم‌های دیگر
    (مثلاً کنترل زوم با فاصله دو دست)، هم برای رسم بصری در core/hand_tracker.py.
    """
    name = "two_hand_frame"

    def __init__(self, config: dict):
        super().__init__(config)
        cfg = config.get("two_hand_frame", {})
        self.stream_rate_hz = cfg.get("stream_rate_hz", 15)
        self._min_interval = 1.0 / max(self.stream_rate_hz, 0.001)
        self._last_emit = 0.0

    def update(self, left_points, right_points, frame_shape, timestamp) -> List[Command]:
        if timestamp - self._last_emit < self._min_interval:
            return []
        self._last_emit = timestamp
        quad = compute_pair_quad(left_points, right_points)
        return [CommandRegistry.make_command("hands.pair.frame", params=quad, hand="Both")]
