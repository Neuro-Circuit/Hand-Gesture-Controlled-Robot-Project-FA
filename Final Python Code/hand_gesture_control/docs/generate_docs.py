"""
اجرای این اسکریپت مستندات کامل تمام دستورات ثبت‌شده در سیستم را
به صورت Markdown و JSON Schema در همین پوشه (docs/) تولید می‌کند.

اجرا:
    python docs/generate_docs.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ایمپورت تمام ماژول‌های حرکت تا دستورات آن‌ها در CommandRegistry ثبت شوند
from core.gestures import (  # noqa: E402
    movement, fist, pinch_rub, finger_point, thumbs, open_palm_swipe, hand_rig, two_hand_frame,
)
from core.command import CommandRegistry  # noqa: E402


def generate():
    registry = CommandRegistry.all()
    out_dir = os.path.dirname(__file__)

    schema_path = os.path.join(out_dir, "commands.schema.json")
    with open(schema_path, "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)

    md_path = os.path.join(out_dir, "commands.md")
    lines = [
        "# مستندات دستورات سیستم تشخیص حرکات دست\n",
        f"تعداد کل دستورات ثبت‌شده: **{len(registry)}**\n",
        "هر دستور یک کد عددی ثابت از صفر به بالا دارد (مناسب خروجی ساده مثل سریال/آردوینو) "
        "و همچنین یک شناسه متنی خوانا برای انسان.\n",
        "| کد | شناسه دستور | نام فارسی | نام انگلیسی | دسته | توضیح | پارامترها |",
        "|---|---|---|---|---|---|---|",
    ]
    for cid, meta in sorted(registry.items(), key=lambda kv: kv[1]["code"]):
        params = ", ".join(f"`{k}`: {v}" for k, v in meta["params_schema"].items()) or "-"
        lines.append(f"| **{meta['code']}** | `{cid}` | {meta['label_fa']} | {meta['label_en']} | "
                      f"{meta['category']} | {meta['description']} | {params} |")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"مستندات با موفقیت تولید شد:\n  - {schema_path}\n  - {md_path}\n"
          f"تعداد دستورات: {len(registry)}")


if __name__ == "__main__":
    generate()
