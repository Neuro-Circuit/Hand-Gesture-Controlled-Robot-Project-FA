"""
سرور وب محلی سبک (Flask) با دو وظیفه:

  1. صفحه‌ای در آدرس مشخص (پیش‌فرض http://127.0.0.1:8000) نمایش می‌دهد که تصویر زنده
     دوربین را با نقاط و خطوط اتصال دست (دقیقاً شبیه دموی خود MediaPipe) نشان می‌دهد،
     به همراه پنل زنده دستورات خروجی.
  2. همان WebSocket موجود (core/output/websocket_sink.py) API بلادرنگ اصلی است؛ این
     سرور فقط یک رابط دیداری روی همان کانال است - هر برنامه دیگری (رباتیک، اسکریپت،
     نرم‌افزار دیگر) هم می‌تواند مستقل و هم‌زمان با این صفحه به همان WebSocket وصل شود.

اجرا در یک ترد جداگانه (daemon) تا حلقه اصلی پردازش تصویر مسدود نشود.
"""
import logging
import threading
import time
import webbrowser

from flask import Flask, Response, render_template

from .broadcaster import FrameBroadcaster

_MJPEG_BOUNDARY = b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"


def create_app(broadcaster: FrameBroadcaster, web_host: str, web_port: int,
               ws_host: str, ws_port: int) -> Flask:
    app = Flask(__name__)
    logging.getLogger("werkzeug").setLevel(logging.ERROR)  # سکوت لاگ پرحجم درخواست‌های MJPEG

    @app.route("/")
    def index():
        return render_template("index.html", web_host=web_host, web_port=web_port,
                                ws_host=ws_host, ws_port=ws_port)

    @app.route("/video_feed")
    def video_feed():
        def generate():
            while True:
                jpeg = broadcaster.get_jpeg()
                if jpeg is not None:
                    yield _MJPEG_BOUNDARY + jpeg + b"\r\n"
                time.sleep(0.03)  # ~30 فریم بر ثانیه سقف پخش به مرورگر

        return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")

    return app


def start_web_server(broadcaster: FrameBroadcaster, config: dict) -> threading.Thread:
    """
    سرور را در یک ترد پس‌زمینه اجرا می‌کند و در صورت فعال بودن auto_open_browser،
    مرورگر پیش‌فرض سیستم را روی آدرس نمایشگر باز می‌کند.
    """
    out_cfg = config.get("output", {})
    web_cfg = out_cfg.get("web", {})
    ws_cfg = out_cfg.get("websocket", {})

    web_host = web_cfg.get("host", "127.0.0.1")
    web_port = web_cfg.get("port", 8000)
    ws_host = ws_cfg.get("host", "127.0.0.1")
    ws_port = ws_cfg.get("port", 8765)

    app = create_app(broadcaster, web_host, web_port, ws_host, ws_port)

    def run():
        app.run(host=web_host, port=web_port, threaded=True, debug=False, use_reloader=False)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()

    url = f"http://{web_host}:{web_port}"
    print(f"[WebServer] نمایشگر زنده در دسترس است: {url}")

    if web_cfg.get("auto_open_browser", True):
        def _open():
            time.sleep(1.0)  # فرصت کوتاه برای بالا آمدن سرور
            webbrowser.open(url)
        threading.Thread(target=_open, daemon=True).start()

    return thread
