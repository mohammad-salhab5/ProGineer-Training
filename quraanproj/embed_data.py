from sentence_transformers import SentenceTransformer

from load_data import load_quran

model = SentenceTransformer("intfloat/multilingual-e5-small")

def embed_verses(verses):

    texts = [v["text"] for v in verses]

    embeddings = model.encode(texts, show_progress_bar=True)

    return embeddings

if __name__ == "__main__":

    verses = load_quran()

    embeddings = embed_verses(verses)

    print("Shape:", embeddings.shape)
