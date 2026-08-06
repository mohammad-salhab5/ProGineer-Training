import chromadb
from sentence_transformers import SentenceTransformer
from text_utils import strip_diacritics

# نفس الموديل بالضبط المستخدم في build_db.py
model = SentenceTransformer("BAAI/bge-m3")

client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_collection("quran")

print("Number of verses:", collection.count())


def retrieve_verses(question, top_k=5):
    cleaned_question = strip_diacritics(question)

    query_embedding = model.encode(
        [cleaned_question],
        normalize_embeddings=True
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )

    print(results["distances"][0])

    verses = []

    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        verses.append({
            "text": doc,
            "reference": meta["reference"]
        })

    return verses


if __name__ == "__main__":
    question = "الصبر"

    results = retrieve_verses(question)

    for r in results:
        print(r["reference"], "-", r["text"])