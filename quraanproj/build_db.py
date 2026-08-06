import chromadb
from load_data import load_quran
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

client = chromadb.PersistentClient(path="./chroma_db")

def build_database():
    # حذف الـ Collection إذا كانت موجودة
    try:
        client.delete_collection("quran")
        print("Old collection deleted.")
    except:
        pass

    # إنشاء Collection جديدة
    collection = client.create_collection("quran")

    verses = load_quran()

    texts = [f"passage: {v['text']}" for v in verses]
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
        texts,
        show_progress_bar=True
    ).tolist()

    batch_size = 1000

    for i in range(0, len(ids), batch_size):
        collection.add(
            ids=ids[i:i + batch_size],
            embeddings=embeddings[i:i + batch_size],
            documents=texts[i:i + batch_size],
            metadatas=metadatas[i:i + batch_size]
        )

    print(f"Added {len(verses)} verses to ChromaDB")

if __name__ == "__main__":
    build_database()