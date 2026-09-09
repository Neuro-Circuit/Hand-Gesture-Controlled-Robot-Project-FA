import threading
from typing import Optional

import cv2


class FrameBroadcaster:
    """
    آخرین فریم تصویرشده (دوربین + نقاط/خطوط اسکلت دست) را به‌صورت JPEG و thread-safe
    نگه می‌دارد. حلقه اصلی پردازش (main.py) هر فریم را اینجا به‌روز می‌کند و سرور وب
    (core/web/server.py) همین بافر را برای پخش زنده MJPEG به مرورگر می‌خواند.

    استفاده از یک قفل ساده کافی است چون فقط آخرین فریم اهمیت دارد؛ نیازی به صف نیست.
    """

    def __init__(self, jpeg_quality: int = 80):
        self._lock = threading.Lock()
        self._jpeg_bytes: Optional[bytes] = None
        self.jpeg_quality = jpeg_quality

    def update(self, frame_bgr) -> None:
        ok, buf = cv2.imencode(".jpg", frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, self.jpeg_quality])
        if not ok:
            return
        with self._lock:
            self._jpeg_bytes = buf.tobytes()

    def get_jpeg(self) -> Optional[bytes]:
        with self._lock:
            return self._jpeg_bytes
