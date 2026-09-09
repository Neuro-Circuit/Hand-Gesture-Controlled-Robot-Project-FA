import math
from typing import List, Tuple

Point = Tuple[float, float, float]  # x, y, z نرمال‌شده (خروجی خام MediaPipe)

# ترتیب ۲۱ نقطه دست دقیقاً مطابق مدل MediaPipe Hands
LANDMARK_NAMES = [
    "WRIST",
    "THUMB_CMC", "THUMB_MCP", "THUMB_IP", "THUMB_TIP",
    "INDEX_MCP", "INDEX_PIP", "INDEX_DIP", "INDEX_TIP",
    "MIDDLE_MCP", "MIDDLE_PIP", "MIDDLE_DIP", "MIDDLE_TIP",
    "RING_MCP", "RING_PIP", "RING_DIP", "RING_TIP",
    "PINKY_MCP", "PINKY_PIP", "PINKY_DIP", "PINKY_TIP",
]

# اندیس (مفصل پایه، مفصل میانی، نوک) برای هر انگشت - برای محاسبه زاویه خمیدگی
FINGER_JOINTS = {
    "thumb":  (1, 2, 3, 4),
    "index":  (5, 6, 7, 8),
    "middle": (9, 10, 11, 12),
    "ring":   (13, 14, 15, 16),
    "pinky":  (17, 18, 19, 20),
}


def to_points(hand_landmarks) -> List[Point]:
    """
    تبدیل خروجی MediaPipe به لیست ساده (x, y, z).
    ورودی معمولاً یک لیست ساده از ۲۱ نقطه است (خروجی مستقیم Tasks API: results.hand_landmarks[i]).
    برای سازگاری، اگر شیء دارای ویژگی .landmark باشد (فرمت قدیمی‌تر) هم پشتیبانی می‌شود.
    """
    if hasattr(hand_landmarks, "landmark"):
        hand_landmarks = hand_landmarks.landmark
    return [(lm.x, lm.y, lm.z) for lm in hand_landmarks]


def distance(a: Point, b: Point) -> float:
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)


def distance_2d(a: Point, b: Point) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def angle_deg(a: Point, b: Point, c: Point) -> float:
    """زاویه در نقطه b بین بردارهای (b->a) و (b->c) بر حسب درجه.
    نزدیک به 180 یعنی مفصل کاملاً صاف (انگشت کشیده)، نزدیک به صفر یعنی کاملاً خم شده."""
    v1 = (a[0] - b[0], a[1] - b[1], a[2] - b[2])
    v2 = (c[0] - b[0], c[1] - b[1], c[2] - b[2])
    dot = v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]
    n1 = math.sqrt(sum(x * x for x in v1))
    n2 = math.sqrt(sum(x * x for x in v2))
    if n1 * n2 == 0:
        return 180.0
    cos_a = max(-1.0, min(1.0, dot / (n1 * n2)))
    return math.degrees(math.acos(cos_a))


def finger_curl_angle(points: List[Point], finger: str) -> float:
    base_i, mid_i, _, tip_i = FINGER_JOINTS[finger]
    return angle_deg(points[base_i], points[mid_i], points[tip_i])


def is_finger_extended(points: List[Point], finger: str, threshold: float = 140.0) -> bool:
    return finger_curl_angle(points, finger) > threshold


def finger_states(points: List[Point], threshold: float = 140.0) -> dict:
    return {f: is_finger_extended(points, f, threshold) for f in FINGER_JOINTS}


def palm_center(points: List[Point]) -> Point:
    idx = [0, 5, 9, 13, 17]
    xs = sum(points[i][0] for i in idx) / len(idx)
    ys = sum(points[i][1] for i in idx) / len(idx)
    zs = sum(points[i][2] for i in idx) / len(idx)
    return (xs, ys, zs)


def hand_size(points: List[Point]) -> float:
    """اندازه تقریبی دست - به عنوان معیار غیرمستقیم عمق (نزدیک/دور از دوربین) استفاده می‌شود،
    چون یک دوربین تک‌چشمی معمولی مقدار عمق واقعی نمی‌دهد."""
    return distance_2d(points[0], points[9]) + distance_2d(points[0], points[17])
