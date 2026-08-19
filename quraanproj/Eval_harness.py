"""
Eval Harness — Quran RAG
=========================

يشغّل مجموعة أسئلة اختبار متنوعة (تغطي أنواع تحدي مختلفة) على كامل
الـ pipeline (optimizer -> retrieval -> reranker -> LLM) دفعة وحدة،
ويحفظ تقرير منظم بملف نصي واحد بدل ما نلحق كل سؤال لحاله.

الهدف: نشوف *نمط* المشاكل (مش عرَض عرَض)، عشان أي إصلاح نسويه يكون
على جذر المشكلة ويتحقق من أثره على كل الأسئلة مرة وحدة، مش سؤال واحد
بس.

طريقة التشغيل:

    python eval_harness.py

بيطلع ملف "eval_report.txt" بنفس المجلد، فيه لكل سؤال:
- التصنيف (أي نوع تحدي بيغطي)
- كامل الـ debug log (optimized query, candidates, reranking..)
- الإجابة النهائية من الـ LLM
- الآيات النهائية المستخدمة

=========================================================
مهم: عدّل الاستيراد تحت حسب اسم ملفك الرئيسي
=========================================================
افترضت إنه اسم الملف اللي فيه ask_quran_bot هو main.py.
إذا كان اسمه مختلف (مثلاً app.py أو bot.py)، غيّر السطر:

    from main import ask_quran_bot

لـ:

    from app import ask_quran_bot   # أو الاسم الصحيح عندك
"""

import io
import contextlib
from datetime import datetime

from ask import ask_quran_bot  # noqa: E402  -- عدّل هاد السطر لو لزم


# =========================================================
# أسئلة الاختبار
#
# كل سؤال مصنّف حسب نوع التحدي اللي بيغطيه، عشان لو صار فشل
# نعرف فورًا هل المشكلة مرتبطة بنوع تحدي معيّن (مصطلح مجرد،
# اسم شائع، استنتاج سببي..) أو عامة بكل النظام.
# =========================================================

TEST_QUESTIONS = [
    {
        "id": 1,
        "category": "سؤال مباشر - إجابة بآية واحدة",
        "question": "من هو النبي الذي ابتلعته الحوت؟",
    },
    {
        "id": 2,
        "category": "سؤال قصصي متعدد الآيات",
        "question": "ما هي الحكم التي تعلمها موسى من رحلته مع الخضر؟",
    },
    {
        "id": 3,
        "category": "مفهوم مجرد غير مذكور حرفيًا بالقرآن",
        "question": "كيف أثبتت براءة مريم بعد إنجاب عيسى؟",
    },
    {
        "id": 4,
        "category": "سؤال سببي / استنتاجي",
        "question": "لماذا طُرد إبليس من رحمة الله؟",
    },
    {
        "id": 5,
        "category": "مقارنة بين قصتين",
        "question": "ما الفرق بين توبة آدم وعصيان إبليس؟",
    },
    {
        "id": 6,
        "category": "كيان جماعي غير اسم شخص",
        "question": "ماذا حدث لأصحاب الكهف عندما ناموا؟",
    },
    {
        "id": 7,
        "category": "كيان غير مذكور بلفظه بالقرآن (اختبار حدود keyword)",
        "question": "من هو الرجل الصالح الذي رافق موسى ولم يُسمَّ صراحة بالقرآن؟",
    },
    {
        "id": 8,
        "category": "سؤال عن معجزة محددة",
        "question": "ما هي معجزة اليد البيضاء لموسى؟",
    },
    {
        "id": 9,
        "category": "سؤال مفهوم عام بدون شخصية محددة",
        "question": "ما هو جزاء الصابرين في القرآن؟",
    },
    {
        "id": 10,
        "category": "سؤال قصة تحتاج تسلسل زمني",
        "question": "كيف بدأت قصة يوسف مع إخوته؟",
    },
    {
        "id": 11,
        "category": "سؤال دقيق برقم / تفصيل",
        "question": "كم عدد السنين التي لبثها أصحاب الكهف نائمين؟",
    },
    {
        "id": 12,
        "category": "مصطلح فقهي/تفسيري مجرد",
        "question": "ما حكم الصبر على الابتلاء في القرآن؟",
    },
    {
        "id": 13,
        "category": "حدث مرتبط بشخصيتين وسبب",
        "question": "لماذا أُلقي إبراهيم في النار؟",
    },
    {
        "id": 14,
        "category": "سؤال بلا إجابة واضحة (اختبار الأمانة / عدم الاختلاق)",
        "question": "ما هو لون قميص يوسف بالتحديد؟",
    },
    {
        "id": 15,
        "category": "سؤال طويل ومركّب (اسم شائع + حدث دقيق)",
        "question": (
            "ما العلامة التي جعلها الله لموسى ليعرف بها مكان "
            "لقائه بالخضر، وماذا فعل موسى عندما نسيها؟"
        ),
    },
]


# =========================================================
# تشغيل سؤال واحد
# =========================================================

def run_single_question(item):
    """
    يشغّل سؤال واحد كامل عبر الـ pipeline، ويلتقط كل الـ print
    الداخلي (من optimize_query و retrieve_verses_hybrid و
    ask_quran_bot نفسها) عن طريق إعادة توجيه stdout مؤقتًا.

    هيك بنحصل على كامل الـ debug log (optimized query,
    candidates, reranking..) داخل التقرير نفسه، بدل ما يضيع
    بالـ console.
    """

    captured = io.StringIO()

    try:
        with contextlib.redirect_stdout(captured):
            answer, verses = ask_quran_bot(item["question"])
        error = None
    except Exception as e:
        answer = None
        verses = []
        error = f"{type(e).__name__}: {e}"

    pipeline_log = captured.getvalue()

    lines = []
    lines.append("=" * 70)
    lines.append(f"TEST #{item['id']} | {item['category']}")
    lines.append("=" * 70)
    lines.append(f"السؤال: {item['question']}")
    lines.append("")

    if error:
        lines.append(f"❌ ERROR: {error}")
        lines.append("")
        # حتى لو صار error، منضيف أي جزء من الـ log انطبع قبل الفشل
        if pipeline_log.strip():
            lines.append("--- PARTIAL PIPELINE LOG ---")
            lines.append(pipeline_log.strip())
            lines.append("")
        return "\n".join(lines)

    lines.append("--- PIPELINE LOG (optimizer + retrieval + reranking) ---")
    lines.append(pipeline_log.strip())
    lines.append("")

    lines.append("--- FINAL ANSWER ---")
    lines.append(answer.strip() if answer else "(no answer)")
    lines.append("")

    lines.append("--- FINAL VERSES USED ---")
    for i, v in enumerate(verses, start=1):
        lines.append(
            f"{i}. {v.get('reference')} "
            f"(surah_ar: {v.get('surah_name_ar')}, "
            f"ayah: {v.get('ayah_number')}) "
            f"| final_score: {round(v.get('final_score', 0.0), 4)} "
            f"| semantic: {round(v.get('semantic_score', 0.0), 4)} "
            f"| keyword: {round(v.get('keyword_score', 0.0), 4)} "
            f"| source: {v.get('source')}"
        )
    lines.append("")

    return "\n".join(lines)


# =========================================================
# تشغيل كل الأسئلة وحفظ التقرير
# =========================================================

def run_eval(output_path="C:\\Users\\hp\\Downloads\\pythonproject\\quraanproj\\Eval_harness.py\\eval_report.txt"):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report_sections = []
    report_sections.append(f"تقرير تقييم Quran RAG — {timestamp}")
    report_sections.append(f"عدد الأسئلة: {len(TEST_QUESTIONS)}")
    report_sections.append("")

    for item in TEST_QUESTIONS:

        print(
            f"⏳ [{item['id']}/{len(TEST_QUESTIONS)}] "
            f"جاري: {item['question'][:60]}..."
        )

        section = run_single_question(item)
        report_sections.append(section)

        print(f"✅ [{item['id']}/{len(TEST_QUESTIONS)}] خلص")

    full_report = "\n".join(report_sections)

    
    print(f"\n📄 التقرير الكامل محفوظ بـ: {output_path}")
    print("   ابعتلي هاد الملف مباشرة.")
    print(full_report)


    return full_report


if __name__ == "__main__":
    run_eval()