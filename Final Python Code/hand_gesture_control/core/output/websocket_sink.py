import asyncio
import json
import threading
from .base_sink import OutputSink
from ..command import Command

try:
    import websockets
except ImportError:
    websockets = None


class WebSocketSink(OutputSink):
    """
    یک سرور وب‌سوکت محلی راه‌اندازی می‌کند تا سایر نرم‌افزارها - حتی نوشته‌شده با
    زبان‌های دیگر (Unity, Unreal, Node.js, رباتیک و ...) - بتوانند بلادرنگ به
    دستورات صادرشده متصل شوند و هرکدام را به حرکت/عمل در سیستم خودشان تبدیل کنند.

    نمونه اتصال از سمت کلاینت پایتون در README.md آمده است.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 8765, categories=None):
        super().__init__(categories)
        if websockets is None:
            raise RuntimeError("کتابخانه websockets نصب نیست: pip install websockets")
        self.host = host
        self.port = port
        self._clients = set()
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def _run_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._start_server())
        self._loop.run_forever()

    async def _start_server(self):
        async def handler(ws):
            self._clients.add(ws)
            try:
                await ws.wait_closed()
            finally:
                self._clients.discard(ws)

        await websockets.serve(handler, self.host, self.port)
        print(f"[WebSocketSink] سرور روی ws://{self.host}:{self.port} در حال اجراست")

    def emit(self, command: Command):
        if not self._clients:
            return
        payload = json.dumps(command.to_dict(), ensure_ascii=False)
        asyncio.run_coroutine_threadsafe(self._broadcast(payload), self._loop)

    async def _broadcast(self, payload: str):
        dead = []
        for ws in list(self._clients):
            try:
                await ws.send(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self._clients.discard(ws)
