"""
توابع هندسی خالص (بدون وابستگی به OpenCV) برای ساخت یک چهارضلعی بین دو دست -
دقیقاً همان الگویی که در دموهای MediaPipe دیده می‌شود: با حرکت دادن دست‌ها، یک
شکل هندسی بین آن‌ها تغییر اندازه/زاویه می‌دهد.

جداسازی این توابع از رسم (cv2) باعث می‌شود هم در تشخیص‌گر (برای ساخت Command) و هم
در HandTracker.draw (برای نمایش بصری) قابل استفاده باشند، بدون وابستگی متقابل.
"""
import math
from typing import Dict, List, Tuple

Point = Tuple[float, float, float]

# اندیس نقطه‌ای که به‌عنوان "بالای دست" استفاده می‌شود (قاعده انگشت اشاره - نقطه‌ای پایدار)
TOP_LANDMARK_INDEX = 5  # INDEX_MCP
WRIST_INDEX = 0


def compute_pair_quad(left_points: List[Point], right_points: List[Point]) -> Dict:
    """
    یک چهارضلعی بین دو دست می‌سازد: دو گوشه پایین از مچ هر دست و دو گوشه بالا از
    قاعده انگشت اشاره (landmark 5) هر دست گرفته می‌شود.

    نکته: ترتیب گوشه‌ها بر اساس موقعیت واقعی x (چپ/راست روی تصویر) تعیین می‌شود، نه
    برچسب handedness ورودی - یعنی حتی اگر left_points/right_points برعکس داده شوند،
    خروجی همیشه هندسی و درست خواهد بود.
    """
    l_wrist, l_top = left_points[WRIST_INDEX], left_points[TOP_LANDMARK_INDEX]
    r_wrist, r_top = right_points[WRIST_INDEX], right_points[TOP_LANDMARK_INDEX]

    if l_wrist[0] > r_wrist[0]:
        l_wrist, r_wrist = r_wrist, l_wrist
        l_top, r_top = r_top, l_top

    bl, tl, tr, br = l_wrist, l_top, r_top, r_wrist
    corners = [bl, tl, tr, br]

    center = (sum(p[0] for p in corners) / 4, sum(p[1] for p in corners) / 4)
    width = _dist(bl, br)
    height = (_dist(bl, tl) + _dist(br, tr)) / 2
    angle_deg = math.degrees(math.atan2(br[1] - bl[1], br[0] - bl[0]))
    area = _shoelace_area(corners)

    return {
        "corners": [[round(p[0], 5), round(p[1], 5)] for p in corners],
        "width": round(width, 5),
        "height": round(height, 5),
        "center": [round(center[0], 5), round(center[1], 5)],
        "angle_deg": round(angle_deg, 2),
        "area": round(area, 6),
    }


def _dist(a: Point, b: Point) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _shoelace_area(pts: List[Point]) -> float:
    n = len(pts)
    s = 0.0
    for i in range(n):
        x1, y1 = pts[i][0], pts[i][1]
        x2, y2 = pts[(i + 1) % n][0], pts[(i + 1) % n][1]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2.0
