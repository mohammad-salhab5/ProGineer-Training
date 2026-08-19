from groq import Groq
from dotenv import load_dotenv
import os

from retrieve import retrieve_verses_hybrid
from retrieve import build_expanded_context
from optimize_questoin import optimize_query
from reranker import rerank_verses


# =========================================================
# Environment
# =========================================================

load_dotenv()


# =========================================================
# Groq
# =========================================================

client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
    timeout=30.0,
)


# =========================================================
# System Prompt
# =========================================================

SYSTEM_PROMPT = """
أنت مساعد متخصص في الإجابة عن القرآن الكريم. مهمتك هي قراءة الآيات المقدمة واستنتاج الإجابة منها.

## استراتيجية الإجابة (الخطوات بالترتيب):
1. **ابحث عن التطابق الحدثي**: إذا كان السؤال يسأل عن "شيء" أو "حدث" محدد، ابحث في الآيات المقدمة عن اللفظ الذي يطابق هذا الشيء/الحدث مباشرة.
2. **لا تخلط بين السياقات**: اسم "موسى" يتكرر في قصص مختلفة. إذا كانت الآيات المقدمة تتحدث عن سياق مختلف (مثل: الطور، النار) ولا تذكر الحدث المطلوب (مثل: الحوت، خرق السفينة)، فتأكد أنها ليست الجواب.
3. **الربط المدعوم**: إذا وجدت آية أساسية تجيب عن السؤال، يمكنك استخدام الآيات الأخرى الداعمة لتوضيح الصورة.
4. **الاعتراف بعدم المعرفة**: إذا لم تجد بين الآيات المقدمة أي آية تذكر الحدث/الشيء المطلوب، أجب بوضوح: "لم ترد في الآيات المقدمة إجابة محددة لهذا السؤال".

## قواعد التوثيق:
- ابدأ إجابتك بالإجابة المختصرة مباشرة.
- استشهد بكل آية تستخدمها بصيغة: (اسم السورة، رقم الآية).
- وضّح سبب كون هذه الآية هي الجواب.

## ملاحظة حول تنسيق الآيات المقدمة:
- كل آية معلَّمة إما [آية مسترجعة أساسية] أو [سياق مجاور].
- الآيات المتتالية بترتيبها الطبيعي بالمصحف.
"""


# =========================================================
# Main Function
# =========================================================

def ask_quran_bot(question):

    # =====================================================
    # 1. Query Optimization
    # =====================================================

    optimized = optimize_query(question)
    optimized["original_question"] = question  # <--- نمرر السؤال الأصلي للـ Router

    print("\n==============================")
    print("ORIGINAL QUESTION")
    print("==============================")

    print(question)

    entities = optimized.get("entities", [])
    concepts = optimized.get("concepts", [])
    search_queries = optimized.get("search_queries", [])
    story_surah_name = optimized.get("story_surah_name", "")
    question_type = optimized.get("question_type", "")

    print("\n==============================")
    print("OPTIMIZED QUERY")
    print("==============================")

    print(f"\nQuestion Type: {question_type}")

    print("\nEntities:")
    print(entities)

    print("\nConcepts:")
    print(concepts)

    print("\nSearch Queries:")
    for i, query in enumerate(search_queries, start=1):
        print(f"{i}. {query}")

    print(f"\nStory Surah: {story_surah_name}")

    # =====================================================
    # 2. Hybrid Retrieval
    # =====================================================

    candidates = retrieve_verses_hybrid(
        optimized=optimized,
        top_k_per_query=12,
        max_dense=40,
        max_keyword=25,
        max_total=60,
    )

    print("\n==============================")
    print("HYBRID RETRIEVAL")
    print("==============================")

    print("Retrieved candidates:", len(candidates))

    print("\n=== ALL CANDIDATES ===")

    for i, verse in enumerate(candidates, start=1):
        print(
            i,
            "|",
            verse.get("reference"),
            "| source:",
            verse.get("source", "unknown"),
            "| distance:",
            round(verse.get("distance", 0.0), 4),
            "| keyword:",
            round(verse.get("keyword_score", 0.0), 4),
            "| query_hits:",
            verse.get("query_hits", 1)
        )

    # =====================================================
    # 3. Reranking
    # =====================================================

    verses = rerank_verses(
        question=question,
        verses=candidates,
        entities=entities,
        surah_name=story_surah_name,
        top_k=8
    )

    print("\n==============================")
    print("RERANKING")
    print("==============================")

    print("Final verses:", len(verses))

    print("\n=== FINAL VERSES ===")

    for i, verse in enumerate(verses, start=1):
        print(
            i,
            "|",
            verse.get("reference"),
            "| semantic:",
            round(verse.get("semantic_score", 0.0), 4),
            "| keyword:",
            round(verse.get("keyword_score", 0.0), 4),
            "| query_hits:",
            verse.get("query_hits", 1),
            "| source:",
            verse.get("source", "unknown"),
            "| final:",
            round(verse.get("final_score", 0.0), 4)
        )

    # =====================================================
    # 4. Build Context
    # =====================================================

    context, expanded_verses = build_expanded_context(
        verses=verses,
        window=2,
    )

    core_count = sum(1 for v in expanded_verses if v.get("is_core"))
    neighbor_count = len(expanded_verses) - core_count

    print("\n==============================")
    print("CONTEXT SENT TO LLM")
    print(
        f"(آيات أساسية: {core_count} | "
        f"سياق مجاور مُضاف: {neighbor_count})"
    )
    print("==============================")

    print(context)

    # =====================================================
    # 5. User Message
    # =====================================================

    user_message = f"""
Retrieved Quran verses:

{context}

Question:
{question}
"""

    # =====================================================
    # 6. Groq / LLM
    # =====================================================

    response = client.chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_message
            }
        ],

        temperature=0,

        max_tokens=300,

        reasoning_effort="low",

        reasoning_format="hidden",
    )

    # =====================================================
    # 7. Final Answer
    # =====================================================

    answer = response.choices[0].message.content

    return (answer, verses)


# =========================================================
# Test
# =========================================================

if __name__ == "__main__":

    question = (
        "ما هي الحكم التي تعلمها سيدنا موسى في رحلته مع الخضر"
    )

    answer, verses = ask_quran_bot(question)

    print("\n==============================")
    print("FINAL ANSWER")
    print("==============================")

    print(answer)