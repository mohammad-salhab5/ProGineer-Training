import chromadb
import streamlit as st

from sentence_transformers import SentenceTransformer

from text_utils import strip_diacritics
from text_utils import normalize_arabic


# =========================================================
# Model
# =========================================================

@st.cache_resource
def load_model():
    return SentenceTransformer("BAAI/bge-m3")


model = load_model()


# =========================================================
# ChromaDB
# =========================================================

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("quran")


# =========================================================
# In-memory keyword index
# =========================================================

@st.cache_resource
def build_keyword_index():
    all_data = collection.get(
        include=["documents", "metadatas"]
    )

    index = []

    for doc, meta in zip(
        all_data["documents"],
        all_data["metadatas"]
    ):
        item = {
            "text": doc,
            "text_normalized": normalize_arabic(doc),
            "meta": meta,
        }
        index.append(item)

    return {
        "items": index,
    }


keyword_index_data = build_keyword_index()
keyword_index = keyword_index_data["items"]


# =========================================================
# Lookup بالـ (surah_id, ayah_number)
# =========================================================

_verse_by_surah_ayah = {}

for item in keyword_index:
    meta = item["meta"]
    surah_id = meta.get("surah_id")
    ayah_number = meta.get("ayah_number")

    if surah_id is None or ayah_number is None:
        continue

    _verse_by_surah_ayah[(surah_id, ayah_number)] = {
        "text": item["text"],
        "surah_id": surah_id,
        "surah_name_ar": meta.get("surah_name_ar"),
        "ayah_number": ayah_number,
        "reference": meta.get("reference"),
    }


# =========================================================
# [Entity Anchors] كشف ديناميكي عام لقصص الكيانات النادرة
# =========================================================

RARE_ENTITY_MAX_OCCURRENCES = 40
STORY_SPAN_WINDOW = 6
MAX_VERSES_PER_ANCHOR_SPAN = 40

SEMANTIC_ANCHOR_TOP_K = 25
SEMANTIC_ANCHOR_MIN_COUNT = 3
SEMANTIC_ANCHOR_MIN_RATIO = 0.30


def _get_semantic_anchor_span(entity_text):
    cleaned = strip_diacritics(entity_text).strip()
    if not cleaned:
        return []

    try:
        query_embedding = model.encode(
            cleaned,
            normalize_embeddings=True,
        ).tolist()

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=SEMANTIC_ANCHOR_TOP_K,
            include=["documents", "metadatas", "distances"],
        )
    except Exception as e:
        print(f"⚠️ Semantic anchor fallback failed for '{entity_text}': {e}")
        return []

    metadatas = results.get("metadatas", [[]])
    metadatas = metadatas[0] if metadatas else []

    if not metadatas:
        return []

    surah_hits = {}
    for meta in metadatas:
        surah_id = meta.get("surah_id")
        ayah_number = meta.get("ayah_number")
        if surah_id is None or ayah_number is None:
            continue
        surah_hits.setdefault(surah_id, []).append(ayah_number)

    if not surah_hits:
        return []

    total_hits = sum(len(v) for v in surah_hits.values())
    dominant_surah, dominant_ayat = max(
        surah_hits.items(),
        key=lambda kv: len(kv[1]),
    )
    ratio = len(dominant_ayat) / total_hits if total_hits else 0.0

    if len(dominant_ayat) < SEMANTIC_ANCHOR_MIN_COUNT or ratio < SEMANTIC_ANCHOR_MIN_RATIO:
        return []

    start_ayah = max(1, min(dominant_ayat) - STORY_SPAN_WINDOW)
    end_ayah = max(dominant_ayat) + STORY_SPAN_WINDOW

    span_verses = []
    added = 0
    for ayah_number in range(start_ayah, end_ayah + 1):
        if added >= MAX_VERSES_PER_ANCHOR_SPAN:
            break
        item = _verse_by_surah_ayah.get((dominant_surah, ayah_number))
        if item is None:
            continue
        span_verses.append({
            "text": item["text"],
            "reference": item["reference"],
            "surah_id": item["surah_id"],
            "surah_name_ar": item["surah_name_ar"],
            "surah_name_translit": None,
            "surah_type": None,
            "ayah_number": item["ayah_number"],
            "distance": 0.35,
            "source": "entity_anchor_semantic",
            "keyword_score": 0.9,
            "keyword_rarity": 1.0,
            "query_hits": 2,
        })
        added += 1

    return span_verses


def _get_entity_anchor_verses(entities):
    if not entities:
        return []

    normalized_entities = [
        (e, normalize_arabic(e))
        for e in entities
        if e and e.strip()
    ]

    if not normalized_entities:
        return []

    anchor_verses = []
    seen_refs = set()

    for original_entity, norm_entity in normalized_entities:
        if not norm_entity:
            continue

        occurrences_by_surah = {}
        for item in keyword_index:
            if norm_entity in item["text_normalized"]:
                meta = item["meta"]
                surah_id = meta.get("surah_id")
                ayah_number = meta.get("ayah_number")
                if surah_id is None or ayah_number is None:
                    continue
                occurrences_by_surah.setdefault(surah_id, []).append(ayah_number)

        total_occurrences = sum(len(ayat) for ayat in occurrences_by_surah.values())

        if total_occurrences == 0:
            semantic_span = _get_semantic_anchor_span(original_entity)
            for item in semantic_span:
                ref = item.get("reference")
                if ref is None or ref in seen_refs:
                    continue
                seen_refs.add(ref)
                anchor_verses.append(item)
            continue

        if total_occurrences > RARE_ENTITY_MAX_OCCURRENCES:
            continue

        for surah_id, ayah_numbers in occurrences_by_surah.items():
            start_ayah = max(1, min(ayah_numbers) - STORY_SPAN_WINDOW)
            end_ayah = max(ayah_numbers) + STORY_SPAN_WINDOW
            added_for_this_span = 0

            for ayah_number in range(start_ayah, end_ayah + 1):
                if added_for_this_span >= MAX_VERSES_PER_ANCHOR_SPAN:
                    break
                item = _verse_by_surah_ayah.get((surah_id, ayah_number))
                if item is None:
                    continue
                ref = item.get("reference")
                if ref is None or ref in seen_refs:
                    continue
                seen_refs.add(ref)
                added_for_this_span += 1
                anchor_verses.append({
                    "text": item["text"],
                    "reference": ref,
                    "surah_id": item["surah_id"],
                    "surah_name_ar": item["surah_name_ar"],
                    "surah_name_translit": None,
                    "surah_type": None,
                    "ayah_number": item["ayah_number"],
                    "distance": 0.3,
                    "source": "entity_anchor",
                    "keyword_score": 1.0,
                    "keyword_rarity": 1.0,
                    "query_hits": 2,
                })

    return anchor_verses


# =========================================================
# Metadata helper
# =========================================================

def _meta_to_verse(
    doc,
    meta,
    distance=0.0,
    source="dense",
    keyword_score=0.0,
    keyword_rarity=1.0,
):
    return {
        "text": doc,
        "reference": meta.get("reference"),
        "surah_id": meta.get("surah_id"),
        "surah_name_ar": meta.get("surah_name_ar"),
        "surah_name_translit": meta.get("surah_name_translit"),
        "surah_type": meta.get("surah_type"),
        "ayah_number": meta.get("ayah_number"),
        "distance": float(distance),
        "source": source,
        "keyword_score": float(keyword_score),
        "keyword_rarity": float(keyword_rarity),
    }


# =========================================================
# build_expanded_context
# =========================================================

def build_expanded_context(verses, window=1):
    if not verses:
        return "", []

    collected = {}

    for verse in verses:
        surah_id = verse.get("surah_id")
        ayah_number = verse.get("ayah_number")

        if surah_id is None or ayah_number is None:
            ref = verse.get("reference") or f"unknown-{id(verse)}"
            collected[("_no_meta_", ref)] = {
                "text": verse.get("text", ""),
                "surah_id": None,
                "surah_name_ar": verse.get("surah_name_ar"),
                "ayah_number": None,
                "reference": ref,
                "is_core": True,
            }
            continue

        for offset in range(-window, window + 1):
            key = (surah_id, ayah_number + offset)
            neighbor = _verse_by_surah_ayah.get(key)
            if neighbor is None:
                continue
            if key not in collected:
                collected[key] = {**neighbor, "is_core": False}
            if offset == 0:
                collected[key]["is_core"] = True

    def sort_key(entry):
        _, v = entry
        if v["surah_id"] is None:
            return (float("inf"), 0)
        return (v["surah_id"], v["ayah_number"])

    ordered = [v for _, v in sorted(collected.items(), key=sort_key)]

    context_lines = []
    prev_surah = None
    prev_ayah = None

    for v in ordered:
        is_contiguous = (
            v["surah_id"] is not None
            and prev_surah == v["surah_id"]
            and prev_ayah is not None
            and v["ayah_number"] == prev_ayah + 1
        )

        if context_lines and not is_contiguous:
            context_lines.append("")

        if v["surah_id"] is not None:
            citation = f"({v['surah_name_ar']}, {v['ayah_number']})"
            prev_surah = v["surah_id"]
            prev_ayah = v["ayah_number"]
        else:
            citation = f"({v['reference']})"
            prev_surah = None
            prev_ayah = None

        tag = "آية مسترجعة أساسية" if v["is_core"] else "سياق مجاور"
        context_lines.append(f"{citation} [{tag}]: {v['text']}")

    context_text = "\n".join(context_lines).strip()
    return context_text, ordered


# =========================================================
# _add_keyword_scores_to_verses
# =========================================================

def _add_keyword_scores_to_verses(verses, entities):
    if not verses:
        return verses

    for verse in verses:
        verse.setdefault("keyword_score", 0.0)
        verse.setdefault("keyword_rarity", 1.0)

    entities_normalized = [
        normalize_arabic(e) for e in (entities or []) if normalize_arabic(e)
    ]

    if not entities_normalized:
        return verses

    total_hits_per_entity = {}
    for item in keyword_index:
        text_norm = item["text_normalized"]
        for entity in entities_normalized:
            if entity in text_norm:
                total_hits_per_entity[entity] = total_hits_per_entity.get(entity, 0) + 1

    for verse in verses:
        text_norm = normalize_arabic(verse["text"])
        matched = [e for e in entities_normalized if e in text_norm]
        if not matched:
            continue

        entity_score = min(1.0, 0.5 + 0.25 * len(matched))
        total_hits = sum(total_hits_per_entity.get(e, 10) for e in matched)
        avg_hits = total_hits / len(matched) if matched else 10
        entity_rarity = min(1.0, 8 / max(avg_hits, 1))

        if entity_score >= verse["keyword_score"]:
            verse["keyword_score"] = entity_score
            verse["keyword_rarity"] = entity_rarity

    return verses


# =========================================================
# _keyword_retrieve_by_terms
# =========================================================

def _keyword_retrieve_by_terms(terms, max_results=25):
    if not terms:
        return []

    terms_normalized = []
    for term in terms:
        normalized_term = normalize_arabic(term) if term else ""
        normalized_term = normalized_term.strip()
        if normalized_term and normalized_term not in terms_normalized:
            terms_normalized.append(normalized_term)

    if not terms_normalized:
        return []

    total_hits_per_term = {}
    matches = []

    for item in keyword_index:
        text_norm = item["text_normalized"]
        matched_terms = [t for t in terms_normalized if t in text_norm]
        if not matched_terms:
            continue
        for term in matched_terms:
            total_hits_per_term[term] = total_hits_per_term.get(term, 0) + 1
        matches.append((item, matched_terms))

    scored_results = []

    for item, matched_terms in matches:
        meta = item["meta"]
        ref = meta.get("reference")
        if ref is None:
            continue

        keyword_score = min(1.0, 0.5 + 0.25 * len(matched_terms))
        total_hits = sum(total_hits_per_term.get(t, 10) for t in matched_terms)
        avg_hits = total_hits / len(matched_terms) if matched_terms else 10
        keyword_rarity = min(1.0, 8 / max(avg_hits, 1))

        verse = _meta_to_verse(
            item["text"],
            meta,
            distance=1.0,
            source="keyword",
            keyword_score=keyword_score,
            keyword_rarity=keyword_rarity,
        )
        verse["query_hits"] = 0
        scored_results.append((keyword_rarity, keyword_score, verse))

    scored_results.sort(key=lambda r: (-r[0], -r[1]))
    return [r[2] for r in scored_results[:max_results]]


# =========================================================
# _build_where_filter
# =========================================================

def _build_where_filter(surah_id=None, surah_name=None):
    conditions = []
    if surah_id is not None:
        conditions.append({"surah_id": surah_id})
    if surah_name is not None:
        conditions.append({"surah_name_ar": surah_name})
    if not conditions:
        return None
    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}


# =========================================================
# _apply_short_verse_penalty
# =========================================================

SHORT_VERSE_MIN_WORDS = 4
SHORT_VERSE_KEYWORD_FLOOR = 0.5
SHORT_VERSE_DISTANCE_PENALTY = 0.15


def _apply_short_verse_penalty(verses):
    for verse in verses:
        text = verse.get("text", "")
        clean_text = strip_diacritics(text).strip()
        word_count = len(clean_text.split()) if clean_text else 0
        keyword_score = float(verse.get("keyword_score", 0.0))
        if word_count < SHORT_VERSE_MIN_WORDS and keyword_score < SHORT_VERSE_KEYWORD_FLOOR:
            verse["distance"] = verse.get("distance", 0.0) + SHORT_VERSE_DISTANCE_PENALTY
            verse["short_verse_penalized"] = True
    return verses


# =========================================================
# retrieve_multi_dense
# =========================================================

def retrieve_multi_dense(
    queries,
    top_k_per_query=12,
    max_total=40,
    surah_id=None,
    surah_name=None,
    trim=True,
):
    if not queries:
        return []

    cleaned_queries = []
    seen_queries = set()

    for query in queries:
        if not query:
            continue
        cleaned = strip_diacritics(query).strip()
        if not cleaned:
            continue
        normalized_key = normalize_arabic(cleaned)
        if normalized_key in seen_queries:
            continue
        seen_queries.add(normalized_key)
        cleaned_queries.append(cleaned)

    if not cleaned_queries:
        return []

    raw_embeddings = model.encode(
        cleaned_queries,
        normalize_embeddings=True,
    ).tolist()

    SIMILARITY_DEDUP_THRESHOLD = 0.92
    deduped_indices = []

    for i, emb_i in enumerate(raw_embeddings):
        is_duplicate = False
        for j in deduped_indices:
            emb_j = raw_embeddings[j]
            similarity = sum(a * b for a, b in zip(emb_i, emb_j))
            if similarity >= SIMILARITY_DEDUP_THRESHOLD:
                is_duplicate = True
                break
        if not is_duplicate:
            deduped_indices.append(i)

    cleaned_queries = [cleaned_queries[i] for i in deduped_indices]
    embeddings = [raw_embeddings[i] for i in deduped_indices]

    where_filter = _build_where_filter(
        surah_id=surah_id,
        surah_name=surah_name,
    )

    query_params = {
        "query_embeddings": embeddings,
        "n_results": top_k_per_query,
        "include": ["documents", "metadatas", "distances"],
    }

    if where_filter is not None:
        query_params["where"] = where_filter

    results = collection.query(**query_params)

    combined = {}

    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])
    distances = results.get("distances", [])

    for query_index in range(len(documents)):
        query_documents = documents[query_index]
        query_metadatas = metadatas[query_index]
        query_distances = distances[query_index]

        for doc, meta, distance in zip(
            query_documents,
            query_metadatas,
            query_distances,
        ):
            ref = meta.get("reference")
            if ref is None:
                continue
            distance = float(distance)

            if ref not in combined:
                combined[ref] = _meta_to_verse(
                    doc,
                    meta,
                    distance=distance,
                    source="dense",
                    keyword_score=0.0,
                )
                combined[ref]["query_hits"] = 1
            else:
                existing = combined[ref]
                if distance < existing["distance"]:
                    existing["distance"] = distance
                existing["query_hits"] = existing.get("query_hits", 1) + 1

    results_list = list(combined.values())
    results_list.sort(
        key=lambda verse: (
            -verse.get("query_hits", 1),
            verse["distance"],
        )
    )

    if not trim:
        return results_list

    return results_list[:max_total]


# =========================================================
# _merge_with_priority
# =========================================================

def _merge_with_priority(dense_results, anchor_verses, anchor_weight=2.0, max_total=60):
    combined = {}
    for v in dense_results:
        ref = v.get("reference")
        if ref:
            combined[ref] = v

    for v in anchor_verses:
        ref = v.get("reference")
        if ref:
            if ref in combined:
                combined[ref]["query_hits"] = combined[ref].get("query_hits", 1) + anchor_weight
                combined[ref]["source"] = combined[ref].get("source", "") + "+anchor"
                combined[ref]["keyword_score"] = max(combined[ref].get("keyword_score", 0.0), 1.0)
                combined[ref]["keyword_rarity"] = max(combined[ref].get("keyword_rarity", 0.0), 1.0)
            else:
                combined[ref] = v
                combined[ref]["query_hits"] = v.get("query_hits", 1) + anchor_weight

    results = list(combined.values())
    results.sort(
        key=lambda v: (
            -v.get("query_hits", 1),
            v.get("distance", 1.0),
        )
    )
    return results[:max_total]


# =========================================================
# الاستراتيجيات الثلاث (الأساسية)
# =========================================================

def _retrieve_story(optimized, top_k_per_query=15, max_total=60):
    """
    استراتيجية القصص (موسى والخضر، أصحاب الكهف، إبراهيم والنار، ...)
    """
    story_surah = optimized.get("story_surah_name", "")
    entities = optimized.get("entities", [])
    concepts = optimized.get("concepts", [])
    literal_anchors = optimized.get("literal_anchor_queries", [])

    queries = literal_anchors.copy()
    
    if "موسى" in entities and "الخضر" in entities:
        event_queries = ["خرقها", "فقتله", "فأقامه"]
        for eq in event_queries:
            if eq not in queries:
                queries.append(eq)
                print(f"ℹ️ [Story] إضافة استعلام حدث: {eq}")
    
    for c in concepts[:3]:
        if c and c not in queries:
            queries.append(c)

    if not queries:
        queries = [optimized.get("original_question", "")]
    
    dense_results = retrieve_multi_dense(
        queries=queries,
        top_k_per_query=top_k_per_query,
        max_total=max_total,
        surah_name=story_surah if story_surah else None,
        trim=False,
    )
    
    anchors = _get_entity_anchor_verses(entities)
    print(f"ℹ️ [Story] تم جلب {len(anchors)} آية من المراسي القصصية")
    
    merged = _merge_with_priority(dense_results, anchors, anchor_weight=2.0, max_total=max_total)
    merged = _add_keyword_scores_to_verses(merged, entities)
    merged = _apply_short_verse_penalty(merged)
    
    return merged


def _retrieve_abstract(optimized, top_k_per_query=20, max_total=60):
    """
    استراتيجية المفاهيم المجردة (الصبر، العدل، الرحمة، الحكمة، ...)
    """
    concepts = optimized.get("concepts", [])
    search_queries = optimized.get("search_queries", [])
    
    queries = search_queries.copy()
    for c in concepts:
        if c and c not in queries:
            queries.append(c)
    
    if not queries:
        queries = [optimized.get("original_question", "")]
    
    dense_results = retrieve_multi_dense(
        queries=queries,
        top_k_per_query=top_k_per_query,
        max_total=max_total,
        surah_name=None,
        trim=False,
    )
    
    keyword_results = _keyword_retrieve_by_terms(concepts, max_results=30)
    
    combined = {}
    for v in dense_results:
        ref = v.get("reference")
        if ref:
            combined[ref] = v
    for v in keyword_results:
        ref = v.get("reference")
        if ref:
            if ref in combined:
                combined[ref]["source"] = combined[ref].get("source", "") + "+keyword"
            else:
                combined[ref] = v
    
    results = list(combined.values())
    results.sort(key=lambda v: (v.get("distance", 1.0), -v.get("query_hits", 1)))
    results = results[:max_total]
    results = _apply_short_verse_penalty(results)
    
    return results


def _retrieve_direct(optimized, top_k_per_query=15, max_total=60):
    """
    استراتيجية الكيان المباشر (أسئلة مثل: من هو موسى؟، أين التقى؟)
    """
    entities = optimized.get("entities", [])
    search_queries = optimized.get("search_queries", [])
    
    queries = search_queries.copy()
    for e in entities:
        if e and e not in queries:
            queries.append(e)
    
    if not queries:
        queries = [optimized.get("original_question", "")]
    
    dense_results = retrieve_multi_dense(
        queries=queries,
        top_k_per_query=top_k_per_query,
        max_total=max_total,
        surah_name=None,
        trim=False,
    )
    
    keyword_results = _keyword_retrieve_by_terms(entities, max_results=25)
    
    combined = {}
    for v in dense_results:
        ref = v.get("reference")
        if ref:
            combined[ref] = v
    for v in keyword_results:
        ref = v.get("reference")
        if ref:
            if ref in combined:
                combined[ref]["source"] = combined[ref].get("source", "") + "+keyword"
            else:
                combined[ref] = v
    
    results = list(combined.values())
    results.sort(key=lambda v: (v.get("distance", 1.0), -v.get("query_hits", 1)))
    results = results[:max_total]
    results = _add_keyword_scores_to_verses(results, entities)
    results = _apply_short_verse_penalty(results)
    
    return results


# =========================================================
# [استراتيجية جديدة] المعجزات (Miracles)
# =========================================================

def _retrieve_miracles(optimized, top_k_per_query=15, max_total=60):
    """
    استراتيجية المعجزات: تبحث عن الآيات التي تصف معجزات الأنبياء.
    خاصة معجزة موسى في الطور (طه، الأعراف، القصص، النازعات).
    """
    entities = optimized.get("entities", [])
    search_queries = optimized.get("search_queries", [])
    
    # بناء استعلامات خاصة بالمعجزات
    queries = []
    
    # إذا كان السؤال عن موسى
    if "موسى" in entities:
        # استعلامات عن معجزات موسى
        miracle_queries = [
            "عصا موسى تلقف ما يأفكون",
            "يد موسى بيضاء", 
            "عصا موسى حية تسعى",
            "موسى نار طور سيناء",
            "ألق عصاك",
            "فألقي عصاه فإذا هي ثعبان مبين",
            "انظر إلى الجبل",
            "تجلى ربه للجبل",
            "كلم الله موسى تكليما",
            "ناداه ربه بالواد المقدس",
            "فأوحينا إلى موسى أن اضرب بعصاك البحر",
            "فلما جاء موسى لميقاتنا وكلمه ربه"
        ]
        queries.extend(miracle_queries)
    
    # إضافة الاستعلامات الأساسية من الـ Optimizer
    for q in search_queries:
        if q and q not in queries:
            queries.append(q)
    
    # إذا لم توجد استعلامات، نضع سؤالاً عاماً
    if not queries:
        queries = [optimized.get("original_question", "معجزات موسى")]
    
    # البحث في كل القرآن (بدون فلتر سورة) لأن المعجزات موجودة في عدة سور
    dense_results = retrieve_multi_dense(
        queries=queries,
        top_k_per_query=top_k_per_query,
        max_total=max_total,
        surah_name=None,  # نبحث في كل القرآن
        trim=False,
    )
    
    # نضيف مراسي إضافية للآيات التي تصف المعجزات
    anchors = _get_entity_anchor_verses(entities)
    merged = _merge_with_priority(dense_results, anchors, anchor_weight=1.5, max_total=max_total)
    merged = _add_keyword_scores_to_verses(merged, entities)
    merged = _apply_short_verse_penalty(merged)
    
    return merged


# =========================================================
# [الموجه الرئيسي] retrieve_verses_hybrid
# =========================================================

def retrieve_verses_hybrid(
    optimized,
    top_k_per_query=12,
    max_dense=40,
    max_keyword=25,
    max_total=60,
    surah_id=None,
    surah_name=None,
    enable_narrative_expansion=True,
):
    if not optimized:
        return []

    # قراءة البيانات الأساسية
    original_question = optimized.get("original_question", "")
    entities = optimized.get("entities", [])
    question_type = optimized.get("question_type", "")
    story_surah_name = optimized.get("story_surah_name", "")
    concepts = optimized.get("concepts", [])
    story_context = optimized.get("story_context", "")

    # =========================================================
    # [تحسين التوجيه] إذا كان السؤال عن موسى ومعجزة
    # =========================================================
    # إذا كان السؤال يحتوي على "موسى" و "معجزة" أو "طور" أو "سيناء"
    if "موسى" in original_question and any(kw in original_question for kw in ["معجزة", "طور", "سيناء", "آية", "برهان"]):
        # تأكد من وجود entities
        if "موسى" not in entities:
            entities.append("موسى")
            optimized["entities"] = entities
            print("ℹ️ [Router] تم إضافة كيان 'موسى' قسراً")
        
        # صنفه كقصصي
        if question_type != "story":
            question_type = "story"
            optimized["question_type"] = "story"
            print("ℹ️ [Router] تم تغيير التصنيف إلى 'story'")
        
        # حدد سورة مناسبة
        if not optimized.get("story_surah_name"):
            if "طور" in original_question or "سيناء" in original_question:
                optimized["story_surah_name"] = "طه"
                print("ℹ️ [Router] تم تعيين سورة 'طه' للقصة")
            else:
                optimized["story_surah_name"] = "طه"
                print("ℹ️ [Router] تم تعيين سورة 'طه' افتراضياً للقصة")

    # =========================================================
    # [التوجيه النهائي] مع مراعاة استراتيجية المعجزات
    # =========================================================
    print("\n" + "="*60)
    print("🔀 RETRIEVAL ROUTER")
    print("="*60)
    print(f"📝 التصنيف من الـ Optimizer: {question_type}")

    # إذا كان السؤال عن معجزة (حتى لو لم يُصنف بشكل صحيح)
    if "معجزة" in original_question and "موسى" in entities:
        print("🌟 استراتيجية: _retrieve_miracles (معجزات)")
        print(f"   - الكيانات: {entities}")
        results = _retrieve_miracles(
            optimized,
            top_k_per_query=15,
            max_total=max_total,
        )
    # التوجيه حسب التصنيف الأصلي
    elif question_type == "story":
        print("📖 استراتيجية: _retrieve_story")
        print(f"   - الكيانات: {entities}")
        print(f"   - السورة المستنتجة: {story_surah_name or 'غير محددة'}")
        results = _retrieve_story(
            optimized,
            top_k_per_query=15,
            max_total=max_total,
        )
    elif question_type == "abstract":
        print("🧠 استراتيجية: _retrieve_abstract")
        print(f"   - المفاهيم: {concepts[:5]}")
        results = _retrieve_abstract(
            optimized,
            top_k_per_query=20,
            max_total=max_total,
        )
    else:  # direct
        print("🎯 استراتيجية: _retrieve_direct")
        print(f"   - الكيانات: {entities}")
        results = _retrieve_direct(
            optimized,
            top_k_per_query=15,
            max_total=max_total,
        )

    print(f"✅ عدد المرشحين المسترجعين: {len(results)}")
    print("="*60 + "\n")

    return results


# =========================================================
# دوال التوافق مع الإصدارات القديمة
# =========================================================

def retrieve_dense(
    question,
    top_k=30,
    surah_id=None,
    surah_name=None,
):
    from text_utils import strip_diacritics
    if not question:
        return []

    cleaned = strip_diacritics(question)
    if not cleaned.strip():
        return []

    query_embedding = model.encode(
        cleaned,
        normalize_embeddings=True,
    ).tolist()

    where_filter = _build_where_filter(
        surah_id=surah_id,
        surah_name=surah_name,
    )

    query_params = {
        "query_embeddings": [query_embedding],
        "n_results": top_k,
        "include": ["documents", "metadatas", "distances"],
    }

    if where_filter is not None:
        query_params["where"] = where_filter

    results = collection.query(**query_params)

    if not results.get("documents") or not results["documents"][0]:
        return []

    verses = []

    for doc, meta, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        verses.append(
            _meta_to_verse(
                doc,
                meta,
                distance=distance,
                source="dense",
                keyword_score=0.0,
            )
        )

    return verses


def retrieve_verses(
    question,
    top_k=20,
    surah_id=None,
    surah_name=None,
):
    return retrieve_dense(
        question=question,
        top_k=top_k,
        surah_id=surah_id,
        surah_name=surah_name,
    )