import math

from sentence_transformers import CrossEncoder
import streamlit as st

from text_utils import strip_diacritics


# =========================================================
# Load Reranker
# =========================================================

@st.cache_resource
def load_reranker():
    return CrossEncoder(
        "BAAI/bge-reranker-v2-m3"
    )


model = load_reranker()


# =========================================================
# Score helpers
# =========================================================

def _normalize_semantic_score(raw_score):
    try:
        return 1.0 / (1.0 + math.exp(-raw_score))
    except OverflowError:
        return 0.0 if raw_score < 0 else 1.0


def _normalize_semantic_scores_batch(raw_scores):
    if not raw_scores:
        return []

    absolute_scores = [
        _normalize_semantic_score(s) for s in raw_scores
    ]

    lo = min(raw_scores)
    hi = max(raw_scores)

    if hi - lo < 1e-9:
        relative_scores = [0.5] * len(raw_scores)
    else:
        relative_scores = [
            (score - lo) / (hi - lo)
            for score in raw_scores
        ]

    return [
        (0.5 * relative) + (0.5 * absolute)
        for relative, absolute in zip(relative_scores, absolute_scores)
    ]


def _compute_final_score(
    semantic_score,
    keyword_score,
    keyword_rarity,
    query_hits,
    verse_text="",
    entities=None,
    surah_name=None,
    verse_surah_name=None,
    ayah_number=None,          # [جديد] رقم الآية
):
    if entities is None:
        entities = []

    normalized_semantic = semantic_score
    query_hit_bonus = min(0.10, 0.03 * max(0, query_hits - 1))

    weighted_keyword_score = keyword_score * keyword_rarity
    keyword_bonus = 0.30 * weighted_keyword_score

    # =========================================================
    # [relation_bonus] فقط إذا وُجدت entities محددة
    # =========================================================
    relation_bonus = 0.0
    if entities and "الخضر" in entities and "موسى" in entities:
        if verse_surah_name == "الكهف":
            # مكافأة أساسية للآيات التي تصف الأحداث (71، 74، 77)
            event_keywords = ["خرق", "سفينة", "غلام", "جدار", "فأراد", "ربك"]
            if any(k in verse_text for k in event_keywords):
                relation_bonus += 0.80
            # مكافأة متوسطة للآيات المحيطة (65-82)
            elif ayah_number and 60 <= ayah_number <= 82:
                relation_bonus += 0.30

    # =========================================================
    # [surah_bonus الذكية] فقط للآيات ضمن النطاق القصصي
    # =========================================================
    surah_bonus = 0.0
    
    # نطاق قصة موسى والخضر: الكهف 60-82
    STORY_RANGE_START = 60
    STORY_RANGE_END = 82
    
    if surah_name and verse_surah_name and surah_name == verse_surah_name:
        # مكافأة السورة فقط إذا كانت الآية ضمن النطاق القصصي
        if ayah_number and STORY_RANGE_START <= ayah_number <= STORY_RANGE_END:
            surah_bonus = 0.50
        elif ayah_number is None:
            # إذا لم نعرف رقم الآية، نعطي مكافأة أقل
            surah_bonus = 0.15

    # =========================================================
    # تجميع النتيجة النهائية
    # =========================================================
    final_score = (
        (normalized_semantic * 0.40)
        + query_hit_bonus
        + keyword_bonus
        + relation_bonus
        + surah_bonus
    )

    return final_score


# =========================================================
# Rerank
# =========================================================

def rerank_verses(
    question,
    verses,
    entities=None,
    surah_name=None,
    top_k=8
):
    if not verses:
        return []

    if entities is None:
        entities = []

    pairs = []

    for verse in verses:
        text = verse.get("text", "").strip()
        if not text:
            continue

        clean_text = strip_diacritics(text).strip()
        pairs.append([
            question,
            clean_text if clean_text else text
        ])

    if not pairs:
        return []

    raw_scores = model.predict(
        pairs,
        show_progress_bar=False
    )

    raw_scores = [float(s) for s in raw_scores]
    normalized_scores = _normalize_semantic_scores_batch(raw_scores)

    scored_verses = []
    score_index = 0

    for verse in verses:
        text = verse.get("text", "").strip()
        if not text:
            continue

        raw_semantic_score = raw_scores[score_index]
        semantic_score = normalized_scores[score_index]
        score_index += 1

        keyword_score = float(verse.get("keyword_score", 0.0))
        keyword_rarity = float(verse.get("keyword_rarity", 1.0))
        query_hits = int(verse.get("query_hits", 1))
        verse_surah_name = verse.get("surah_name_ar")
        ayah_number = verse.get("ayah_number")  # [جديد] استخراج رقم الآية

        final_score = _compute_final_score(
            semantic_score=semantic_score,
            keyword_score=keyword_score,
            keyword_rarity=keyword_rarity,
            query_hits=query_hits,
            verse_text=text,
            entities=entities,
            surah_name=surah_name,
            verse_surah_name=verse_surah_name,
            ayah_number=ayah_number,  # [جديد] تمرير رقم الآية
        )

        scored_verses.append({
            **verse,
            "semantic_score": semantic_score,
            "raw_semantic_score": raw_semantic_score,
            "keyword_score": keyword_score,
            "keyword_rarity": keyword_rarity,
            "query_hits": query_hits,
            "source": verse.get("source", "unknown"),
            "final_score": final_score,
        })

    scored_verses.sort(
        key=lambda x: x["final_score"],
        reverse=True
    )

    return scored_verses[:top_k]