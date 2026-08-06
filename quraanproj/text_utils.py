import re

# نطاق يونيكود لعلامات التشكيل العربي (الحركات، الشدة، السكون، التنوين...)
_ARABIC_DIACRITICS = re.compile(r'[\u0610-\u061A\u064B-\u065F\u06D6-\u06DC\u06DF-\u06E8\u06EA-\u06ED\u08D4-\u08E1\u08E3-\u08FF]')
_TATWEEL = '\u0640'

def strip_diacritics(text: str) -> str:
    """يشيل التشكيل والتطويل من النص، للاستخدام وقت توليد الـ embedding فقط.
    النص الأصلي المُشكّل بيضل محفوظ لغايات العرض للمستخدم."""
    text = _ARABIC_DIACRITICS.sub('', text)
    text = text.replace(_TATWEEL, '')
    return text
