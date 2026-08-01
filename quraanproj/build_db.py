import chromadb

from load_data import load_quran

from sentence_transformers import SentenceTransformer

model = SentenceTransformer("intfloat/multilingual-e5-small")

client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection("quran")

def build_database():

    verses = load_quran()

    texts = [v["text"] for v in verses]

    ids = [str(i) for i in range(len(verses))]

    metadatas = [

        {

            "reference": v["reference"],

            "surah_name": v["surah_name_translit"],

            "ayah_number": v["ayah_number"]

        }

        for v in verses

    ]

    embeddings = model.encode(texts, show_progress_bar=True).tolist()

    collection.add(

        ids=ids,

        embeddings=embeddings,

        documents=texts,

        metadatas=metadatas

    )

    print(f"Added {len(verses)} verses to ChromaDB")

if __name__ == "__main__":

    build_database()
