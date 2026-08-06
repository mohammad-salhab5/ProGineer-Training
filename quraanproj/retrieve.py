import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_collection("quran")

print("Number of verses:", collection.count())


def retrieve_verses(question, top_k=5):
    query_embedding = model.encode(
        [f"query: {question}"],
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
    question = ""

    results = retrieve_verses(question)

    for r in results:
        print(r["reference"], "-", r["text"])