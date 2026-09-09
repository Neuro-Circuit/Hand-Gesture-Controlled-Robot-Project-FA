import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Optional


@dataclass
class Command:
    """
    ساختار استاندارد یک دستور خروجی.
    هر حرکت تشخیص داده‌شده - چه یک رخداد گسسته (مثل مشت کردن) و چه یک فریم کامل
    داده ریگ دست - در قالب همین کلاس بسته‌بندی و به سینک‌های خروجی ارسال می‌شود.

    فیلد `code`: یک عدد صحیح ثابت و یکتا برای هر نوع دستور (از صفر شروع می‌شود).
    این کد برای اتصال به سیستم‌های ساده‌تر (مثل ارتباط سریال با آردوینو/رباتیک) در
    نظر گرفته شده که فقط یک عدد به‌جای یک شیء کامل JSON نیاز دارند.
    """
    command_id: str
    code: int
    label_fa: str
    label_en: str
    category: str
    params: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    hand: str = "Right"
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CommandRegistry:
    """
    رجیستری مرکزی تمام دستورات ممکن در سیستم.
    هر تشخیص‌گر حرکت هنگام بارگذاری، دستور(های) خودش را اینجا با یک شناسه متنی
    و یک کد عددی یکتا ثبت می‌کند. از روی همین رجیستری، مستندات Markdown و
    JSON Schema به‌طور خودکار تولید می‌شود.

    کدهای عددی عمداً در همین‌جا (کنار محل تعریف هر دستور، داخل هر فایل gestures/*.py)
    به‌صورت صریح مشخص می‌شوند، نه به‌صورت خودکار بر اساس ترتیب import - تا همیشه
    ثابت، قابل پیش‌بینی و قابل کنترل توسط توسعه‌دهنده باقی بمانند.
    """
    _registry: Dict[str, Dict[str, Any]] = {}
    _codes_used: Dict[int, str] = {}

    @classmethod
    def register(cls, command_id: str, code: int, label_fa: str, label_en: str,
                 category: str, description: str,
                 params_schema: Optional[Dict[str, str]] = None):
        existing_owner = cls._codes_used.get(code)
        if existing_owner is not None and existing_owner != command_id:
            raise ValueError(
                f"تداخل کد: کد {code} قبلاً به دستور '{existing_owner}' اختصاص یافته "
                f"و نمی‌تواند دوباره به '{command_id}' داده شود. یک کد یکتای دیگر انتخاب کنید."
            )
        cls._codes_used[code] = command_id
        cls._registry[command_id] = {
            "command_id": command_id,
            "code": code,
            "label_fa": label_fa,
            "label_en": label_en,
            "category": category,
            "description": description,
            "params_schema": params_schema or {},
        }

    @classmethod
    def all(cls) -> Dict[str, Dict[str, Any]]:
        return cls._registry

    @classmethod
    def make_command(cls, command_id: str, params: Optional[Dict[str, Any]] = None,
                      confidence: float = 1.0, hand: str = "Right") -> Command:
        """
        ساخت یک Command کامل فقط از روی شناسه متنی؛ بقیه فیلدها (کد، برچسب‌ها، دسته)
        به‌طور خودکار از رجیستری خوانده می‌شوند - تا اطلاعات هر دستور فقط در یک جا
        (فراخوانی register) تعریف شود و در کد تشخیص‌گرها تکرار نشود.
        """
        meta = cls._registry.get(command_id)
        if meta is None:
            raise KeyError(f"دستور '{command_id}' ثبت نشده است. ابتدا با CommandRegistry.register ثبت کنید.")
        return Command(
            command_id=command_id,
            code=meta["code"],
            label_fa=meta["label_fa"],
            label_en=meta["label_en"],
            category=meta["category"],
            params=params or {},
            confidence=confidence,
            hand=hand,
        )
