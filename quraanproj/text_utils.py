import re

_ARABIC_DIACRITICS = re.compile(r'[\u064B-\u0652\u0670\u06D6-\u06ED]')
_TATWEEL = '\u0640'

_ALEF_VARIANTS = re.compile(r'[إأآا]')
_YA_VARIANTS = re.compile(r'ى')
_TA_MARBUTA = re.compile(r'ة')


def strip_diacritics(text: str) -> str:
    """يشيل التشكيل والتطويل من النص، للاستخدام وقت توليد الـ embedding
    ووقت البحث النصي (keyword matching) فقط. النص الأصلي المُشكّل
    بيضل محفوظ لغايات العرض للمستخدم."""

    text = _ARABIC_DIACRITICS.sub('', text)
    text = text.replace(_TATWEEL, '')

    return text


def normalize_arabic(text: str) -> str:
    """تطبيع إضافي لتوحيد أشكال الألف/الهمزة والياء، خصيصاً
    للاستخدام في مطابقة الكلمات المفتاحية (entity matching) حيث
    الفرق بين "إبراهيم" و"ابراهيم" لازم يُعتبر تطابق."""

    text = strip_diacritics(text)
    text = _ALEF_VARIANTS.sub('ا', text)
    text = _YA_VARIANTS.sub('ي', text)
    # ⚠️ لا تطبّق _TA_MARBUTA هون إذا بيأثر على معنى الكلمة
    # (مثلاً "فاطمة" vs "فاطمه" - عادة نادراً ما تسبب مشكلة، اختياري)

    return text

def build_contextual_embedding_texts(verses, window=1):
    """
    لكل آية، نبني نص embedding يتضمن الآيات المجاورة (قبل وبعد)
    ضمن نفس السورة، عشان الـ embedding يلتقط السياق القصصي/الموضوعي
    بدل ما يعتمد على الآية المعزولة لحالها فقط.

    النص المعروض (clean_display_texts) بيضل زي ما هو - آية واحدة فقط.
    بس النص يلي بينعمله embed بيصير أوسع.
    """

    texts = []

    for i, v in enumerate(verses):

        start = max(0, i - window)
        end = min(len(verses), i + window + 1)

        # لازم نتأكد إن الآيات المجاورة من نفس السورة
        context_verses = [
            verses[j]["text"]
            for j in range(start, end)
            if verses[j]["surah_id"] == v["surah_id"]
        ]

        context_text = " ".join(context_verses)

        texts.append(strip_diacritics(context_text))

    return texts