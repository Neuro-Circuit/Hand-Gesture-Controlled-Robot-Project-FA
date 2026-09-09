from .base_sink import OutputSink
from ..command import Command


class ConsoleSink(OutputSink):
    """
    چاپ دستورات در کنسول - با دو حالت:

    mode="numeric" (پیش‌فرض): فقط کد عددی دستور در یک خط چاپ می‌شود، مثلاً:
        0
        1
        4
    این حالت برای اتصال ساده به اسکریپت‌ها یا سیستم‌های دیگر (مثل خواندن از پایپ
    توسط یک برنامه سریال/آردوینو) طراحی شده.

    mode="full": خروجی کامل و خواناتر شامل کد، شناسه متنی، برچسب فارسی/انگلیسی و پارامترها
    (همان چیزی که برای دیباگ توسعه‌دهنده مفید است).
    """

    def __init__(self, categories=None, mode: str = "numeric"):
        super().__init__(categories)
        self.mode = mode

    def emit(self, command: Command):
        if self.mode == "numeric":
            print(command.code)
        else:
            params = f" params={command.params}" if command.params else ""
            print(f"[{command.timestamp:.2f}] code={command.code:<3d} {command.command_id:28s} "
                  f"({command.label_fa} / {command.label_en}) hand={command.hand}{params}")
