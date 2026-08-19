import chromadb

from load_data import load_quran
from sentence_transformers import SentenceTransformer
from text_utils import strip_diacritics
from text_utils import  build_contextual_embedding_texts


# BGE-M3
model = SentenceTransformer("BAAI/bge-m3")


client = chromadb.PersistentClient(
    path="./chroma_db"
)


def build_database():

    # حذف الـ Collection القديمة
    try:
        client.delete_collection("quran")
        print("Old collection deleted.")
    except Exception:
        pass


    # إنشاء Collection جديدة
    collection = client.create_collection(
        "quran",
        metadata={"hnsw:space": "cosine"}
    )


    # تحميل القرآن
    verses = load_quran()


    # النص الأصلي للتخزين والعرض
    clean_display_texts = [
        v["text"]
        for v in verses
    ]


    # النص المستخدم للـembedding
    embedding_texts = build_contextual_embedding_texts(verses, window=1)


    # IDs
    ids = [
        str(i)
        for i in range(len(verses))
    ]


    # Metadata
    metadatas = [
        {
            "reference": v["reference"],
            "surah_id": v["surah_id"],
            "surah_name_ar": v["surah_name_ar"],
            "surah_name_translit": v["surah_name_translit"],
            "surah_type": v["surah_type"],
            "ayah_number": v["ayah_number"]
        }
        for v in verses
    ]


    # Generate embeddings
    embeddings = model.encode(
        embedding_texts,
        show_progress_bar=True,
        normalize_embeddings=True
    ).tolist()


    # إضافة البيانات على دفعات
    batch_size = 1000

    for i in range(0, len(ids), batch_size):

        collection.add(
            ids=ids[i:i + batch_size],
            embeddings=embeddings[i:i + batch_size],
            documents=clean_display_texts[i:i + batch_size],
            metadatas=metadatas[i:i + batch_size]
        )


    print(
        f"Added {len(verses)} verses to ChromaDB"
    )


if __name__ == "__main__":
    build_database()