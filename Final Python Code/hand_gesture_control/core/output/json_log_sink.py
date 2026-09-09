import json
import os
from .base_sink import OutputSink
from ..command import Command


class JSONLogSink(OutputSink):
    """
    هر دستور را بلادرنگ به صورت یک خط JSON در فایل ذخیره می‌کند (فرمت JSON Lines).
    این فایل بعداً برای بازپخش، تحلیل، یا آموزش/تست سایر بخش‌های سیستم قابل استفاده است.
    """

    def __init__(self, path: str, categories=None):
        super().__init__(categories)
        self.path = path
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self._file = open(path, "a", encoding="utf-8")

    def emit(self, command: Command):
        self._file.write(json.dumps(command.to_dict(), ensure_ascii=False) + "\n")
        self._file.flush()

    def close(self):
        self._file.close()
