"""
پوششی روی MediaPipe Tasks HandLandmarker.

توجه مهم: MediaPipe از اوایل ۲۰۲۳ به‌تدریج API قدیمی‌تر 'mp.solutions.hands' را منسوخ
اعلام کرده بود و در نسخه‌های اخیر pip (مثلاً 0.10.33) کاملاً حذف شده و دیگر در دسترس
نیست (باعث AttributeError می‌شود). به همین دلیل این ماژول از API جدید و رسمی «Tasks»
استفاده می‌کند که به یک فایل مدل (hand_landmarker.task) نیاز دارد؛ این فایل در اولین
اجرا به‌طور خودکار از سرور گوگل دانلود و در پوشه models/ کش می‌شود.
"""
import os
import time
import urllib.request

import cv2
import mediapipe as mp

from .landmarks import to_points
from .two_hand_geometry import compute_pair_quad

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

MODEL_URL = ("https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
             "hand_landmarker/float16/latest/hand_landmarker.task")
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "hand_landmarker.task")

# اتصالات استاندارد بین ۲۱ نقطه دست برای رسم اسکلت روی تصویر.
# چون drawing_utils قدیمی (mp.solutions.drawing_utils) دیگر در دسترس نیست، این اتصالات
# را مستقیماً با OpenCV رسم می‌کنیم.
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),          # شست
    (0, 5), (5, 6), (6, 7), (7, 8),          # اشاره
    (5, 9), (9, 10), (10, 11), (11, 12),     # میانی
    (9, 13), (13, 14), (14, 15), (15, 16),   # حلقه
    (13, 17), (17, 18), (18, 19), (19, 20),  # کوچک
    (0, 17),                                  # مچ تا قاعده انگشت کوچک
]


def ensure_model_downloaded(path: str = MODEL_PATH, url: str = MODEL_URL) -> str:
    """اگر مدل قبلاً دانلود نشده، یک‌بار (حدود ۷-۱۰ مگابایت) از سرور گوگل دانلود می‌کند."""
    if os.path.exists(path):
        return path
    os.makedirs(os.path.dirname(path), exist_ok=True)
    print(f"[HandTracker] در حال دانلود مدل تشخیص دست (یک‌بار انجام می‌شود) از:\n  {url}")
    urllib.request.urlretrieve(url, path)
    print(f"[HandTracker] مدل با موفقیت ذخیره شد در: {path}")
    return path


class HandTracker:
    def __init__(self, config: dict):
        cam_cfg = config.get("camera", {})
        model_path = cam_cfg.get("model_path") or ensure_model_downloaded()

        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.VIDEO,
            num_hands=cam_cfg.get("max_num_hands", 1),
            min_hand_detection_confidence=cam_cfg.get("min_detection_confidence", 0.6),
            min_tracking_confidence=cam_cfg.get("min_tracking_confidence", 0.5),
        )
        self.landmarker = HandLandmarker.create_from_options(options)
        self._start_time = time.time()

    def process(self, frame_bgr):
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        timestamp_ms = int((time.time() - self._start_time) * 1000)
        return self.landmarker.detect_for_video(mp_image, timestamp_ms)

    def draw(self, frame_bgr, results):
        if not results.hand_landmarks:
            return frame_bgr
        h, w = frame_bgr.shape[:2]
        for hand_landmarks in results.hand_landmarks:
            pts = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks]
            for a, b in HAND_CONNECTIONS:
                cv2.line(frame_bgr, pts[a], pts[b], (0, 200, 0), 2)
            for x, y in pts:
                cv2.circle(frame_bgr, (x, y), 4, (0, 0, 255), -1)

        # وقتی هر دو دست هم‌زمان دیده شوند، شکل هندسی بین آن‌ها رسم می‌شود
        # (همان چهارضلعی که TwoHandFrameDetector هم به‌عنوان دستور خروجی می‌سازد)
        if len(results.hand_landmarks) == 2:
            p0 = to_points(results.hand_landmarks[0])
            p1 = to_points(results.hand_landmarks[1])
            quad = compute_pair_quad(p0, p1)
            corners_px = [(int(x * w), int(y * h)) for x, y in quad["corners"]]
            for i in range(4):
                cv2.line(frame_bgr, corners_px[i], corners_px[(i + 1) % 4], (255, 255, 255), 2)
            cx, cy = int(quad["center"][0] * w), int(quad["center"][1] * h)
            cv2.circle(frame_bgr, (cx, cy), 3, (255, 255, 255), -1)

        return frame_bgr

    def close(self):
        self.landmarker.close()
