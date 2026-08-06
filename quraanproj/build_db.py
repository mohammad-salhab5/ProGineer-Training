import chromadb
from load_data import load_quran
from sentence_transformers import SentenceTransformer
from text_utils import strip_diacritics

# BGE-M3: موديل مخصص لمهام الاسترجاع (retrieval)، بيدعم العربي بقوة
# ملاحظة: BGE-M3 ما بيحتاج بادئات query:/passage: زي e5
model = SentenceTransformer("BAAI/bge-m3")

client = chromadb.PersistentClient(path="./chroma_db")

def build_database():
    # حذف الـ Collection إذا كانت موجودة
    try:
        client.delete_collection("quran")
        print("Old collection deleted.")
    except:
        pass

    # إنشاء Collection جديدة - مهم: تحديد cosine كمسافة التشابه
    collection = client.create_collection(
        "quran",
        metadata={"hnsw:space": "cosine"}
    )

    verses = load_quran()

    # النص المخزن كـ document = النص الأصلي المُشكّل (للعرض للمستخدم)
    clean_display_texts = [v["text"] for v in verses]

    # نص الـ embedding = بدون تشكيل (بدون بادئة، BGE-M3 ما بيحتاجها)
    embedding_texts = [strip_diacritics(v["text"]) for v in verses]

    ids = [str(i) for i in range(len(verses))]

    metadatas = [
        {
            "reference": v["reference"],
            "surah_name": v["surah_name_translit"],
            "ayah_number": v["ayah_number"]
        }
        for v in verses
    ]

    embeddings = model.encode(
        embedding_texts,
        show_progress_bar=True,
        normalize_embeddings=True  # لازم يطابق التطبيع في retrieve.py
    ).tolist()

    batch_size = 1000

    for i in range(0, len(ids), batch_size):
        collection.add(
            ids=ids[i:i + batch_size],
            embeddings=embeddings[i:i + batch_size],
            documents=clean_display_texts[i:i + batch_size],
            metadatas=metadatas[i:i + batch_size]
        )

    print(f"Added {len(verses)} verses to ChromaDB")

if __name__ == "__main__":
    build_database()