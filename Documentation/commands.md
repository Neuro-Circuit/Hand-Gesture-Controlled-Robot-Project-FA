# مستندات دستورات سیستم تشخیص حرکات دست

تعداد کل دستورات ثبت‌شده: **19**

هر دستور یک کد عددی ثابت از صفر به بالا دارد (مناسب خروجی ساده مثل سریال/آردوینو) و همچنین یک شناسه متنی خوانا برای انسان.

| کد | شناسه دستور | نام فارسی | نام انگلیسی | دسته | توضیح | پارامترها |
|---|---|---|---|---|---|---|
| **0** | `finger.swipe.down` | حرکت انگشت اشاره به پایین | Finger Swipe Down | gesture | در حالت اشاره‌کردن، نوک انگشت اشاره به پایین حرکت می‌کند | `speed`: float |
| **1** | `finger.swipe.up` | حرکت انگشت اشاره به بالا | Finger Swipe Up | gesture | در حالت اشاره‌کردن، نوک انگشت اشاره به بالا حرکت می‌کند | `speed`: float |
| **2** | `finger.swipe.left` | حرکت انگشت اشاره به چپ | Finger Swipe Left | gesture | در حالت اشاره‌کردن، نوک انگشت اشاره به چپ حرکت می‌کند | `speed`: float |
| **3** | `finger.swipe.right` | حرکت انگشت اشاره به راست | Finger Swipe Right | gesture | در حالت اشاره‌کردن، نوک انگشت اشاره به راست حرکت می‌کند | `speed`: float |
| **4** | `hand.fist` | مشت کردن دست | Fist | gesture | چهار انگشت اشاره تا کوچک کاملاً جمع می‌شوند | - |
| **5** | `hand.open` | باز کردن دست | Open Hand | gesture | دست از حالت مشت خارج و باز می‌شود | - |
| **6** | `hand.move.left` | حرکت دست به چپ | Hand Move Left | movement | مرکز کف دست به سمت چپ جابه‌جا می‌شود | `speed`: float |
| **7** | `hand.move.right` | حرکت دست به راست | Hand Move Right | movement | مرکز کف دست به سمت راست جابه‌جا می‌شود | `speed`: float |
| **8** | `hand.move.up` | حرکت دست به بالا | Hand Move Up | movement | مرکز کف دست به سمت بالا جابه‌جا می‌شود | `speed`: float |
| **9** | `hand.move.down` | حرکت دست به پایین | Hand Move Down | movement | مرکز کف دست به سمت پایین جابه‌جا می‌شود | `speed`: float |
| **10** | `hand.move.forward` | حرکت دست به جلو | Hand Move Forward | movement | دست به دوربین نزدیک می‌شود (بر اساس بزرگ‌تر شدن اندازه دست) | `speed`: float |
| **11** | `hand.move.backward` | حرکت دست به عقب | Hand Move Backward | movement | دست از دوربین دور می‌شود (بر اساس کوچک‌تر شدن اندازه دست) | `speed`: float |
| **12** | `hand.pinch.start` | شروع نزدیک کردن شست و اشاره | Pinch Start | gesture | نوک شست و نوک اشاره به هم نزدیک می‌شوند | - |
| **13** | `hand.pinch.rub` | مالیدن شست و اشاره به هم | Pinch Rub | gesture | دو انگشت در حالت نزدیک، حرکت رفت‌وبرگشتی (مالش) انجام می‌دهند | `intensity`: float |
| **14** | `hand.pinch.end` | پایان نزدیک کردن شست و اشاره | Pinch End | gesture |  | - |
| **15** | `hand.thumb.show` | نشان دادن انگشت شست | Thumb Shown | gesture | فقط انگشت شست کشیده و چهار انگشت دیگر جمع هستند | `direction`: str |
| **16** | `hand.thumb.hide` | پنهان شدن انگشت شست | Thumb Hidden | gesture |  | - |
| **17** | `hand.open_palm.swipe_right` | حرکت دست باز به راست | Open Palm Swipe Right | gesture | تمام پنج انگشت باز هستند و کل دست به سمت راست حرکت می‌کند | `speed`: float |
| **18** | `hand.rig.frame` | داده کامل ریگ دست | Full Hand Rig Frame | rig | موقعیت هر ۲۱ نقطه دست (دقیقاً مطابق خروجی خام MediaPipe) به همراه زاویه خمیدگی و وضعیت کشیده/جمع هر انگشت، در هر فریم (یا با نرخ محدودشده) صادر می‌شود. برای اتصال به مدل سه‌بعدی/ریگ کاراکتر، رباتیک یا هر مصرف‌کننده‌ای که به داده خام نیاز دارد. | `landmarks`: آرایه‌ای از ۲۱ نقطه [x, y, z] نرمال‌شده، به ترتیب استاندارد MediaPipe, `landmarks_named`: همان ۲۱ نقطه با کلید نام مفصل (مثل INDEX_TIP), `finger_states`: دیکشنری بولین extended/curled برای هر انگشت, `finger_curl_angles`: زاویه خمیدگی هر انگشت بر حسب درجه (180=کاملاً صاف), `palm_center`: [x, y, z] مرکز کف دست, `hand_size`: اندازه تقریبی دست - قابل استفاده برای تخمین عمق/فاصله از دوربین |
