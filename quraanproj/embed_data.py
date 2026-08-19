from sentence_transformers import SentenceTransformer

from load_data import load_quran
from text_utils import strip_diacritics


model = SentenceTransformer("BAAI/bge-m3")


def embed_verses(verses):

    # إزالة التشكيل قبل إنشاء الـembeddings
    texts = [
        strip_diacritics(v["text"])
        for v in verses
    ]

    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    return embeddings


if __name__ == "__main__":

    verses = load_quran()

    embeddings = embed_verses(verses)

    print("Shape:", embeddings.shape)

    print(
        "Embedding dimension:",
        len(embeddings[0])
    )

    print(
        "First 5 values:",
        embeddings[0][:5]
    )