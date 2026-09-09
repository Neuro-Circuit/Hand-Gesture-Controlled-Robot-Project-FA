from typing import List
from ..gesture_base import GestureDetector
from ..command import Command, CommandRegistry
from ..landmarks import finger_states, finger_curl_angle, palm_center, hand_size, LANDMARK_NAMES, FINGER_JOINTS

CommandRegistry.register(
    "hand.rig.frame", 18, "داده کامل ریگ دست", "Full Hand Rig Frame", "rig",
    "موقعیت هر ۲۱ نقطه دست (دقیقاً مطابق خروجی خام MediaPipe) به همراه زاویه خمیدگی "
    "و وضعیت کشیده/جمع هر انگشت، در هر فریم (یا با نرخ محدودشده) صادر می‌شود. "
    "برای اتصال به مدل سه‌بعدی/ریگ کاراکتر، رباتیک یا هر مصرف‌کننده‌ای که به داده خام نیاز دارد.",
    {
        "landmarks": "آرایه‌ای از ۲۱ نقطه [x, y, z] نرمال‌شده، به ترتیب استاندارد MediaPipe",
        "landmarks_named": "همان ۲۱ نقطه با کلید نام مفصل (مثل INDEX_TIP)",
        "finger_states": "دیکشنری بولین extended/curled برای هر انگشت",
        "finger_curl_angles": "زاویه خمیدگی هر انگشت بر حسب درجه (180=کاملاً صاف)",
        "palm_center": "[x, y, z] مرکز کف دست",
        "hand_size": "اندازه تقریبی دست - قابل استفاده برای تخمین عمق/فاصله از دوربین",
    },
)


class HandRigEmitter(GestureDetector):
    """
    برخلاف بقیه تشخیص‌گرها که فقط لحظه وقوع یک رویداد خاص را اعلام می‌کنند،
    این کلاس در هر فریم (با نرخ قابل‌تنظیم stream_rate_hz) تمام داده اسکلتی دست
    را در قالب یک Command استاندارد صادر می‌کند - یعنی هرچه MediaPipe به‌صورت خام
    می‌دهد، اینجا مستندسازی‌شده و آماده مصرف بلادرنگ توسط سیستم‌های دیگر است.
    """
    name = "hand_rig"

    def __init__(self, config: dict):
        super().__init__(config)
        cfg = config.get("hand_rig", {})
        self.enabled = cfg.get("enabled", True)
        self.stream_rate_hz = cfg.get("stream_rate_hz", 15)
        self._min_interval = 1.0 / max(self.stream_rate_hz, 0.001)
        self._last_emit = 0.0

    def update(self, points, frame_shape, timestamp, hand_label) -> List[Command]:
        if not self.enabled:
            return []
        if timestamp - self._last_emit < self._min_interval:
            return []
        self._last_emit = timestamp

        states = finger_states(points)
        curl_angles = {f: round(finger_curl_angle(points, f), 1) for f in FINGER_JOINTS}
        landmarks = [[round(p[0], 5), round(p[1], 5), round(p[2], 5)] for p in points]
        landmarks_named = {LANDMARK_NAMES[i]: landmarks[i] for i in range(len(landmarks))}

        return [CommandRegistry.make_command(
            "hand.rig.frame",
            params={
                "landmarks": landmarks,
                "landmarks_named": landmarks_named,
                "finger_states": states,
                "finger_curl_angles": curl_angles,
                "palm_center": list(palm_center(points)),
                "hand_size": round(hand_size(points), 5),
            },
            hand=hand_label,
        )]
