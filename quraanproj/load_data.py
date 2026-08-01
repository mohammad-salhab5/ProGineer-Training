import json

def load_quran(path="data/quran_flat.json"):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

if __name__ == "__main__":
    verses = load_quran()

    print(f"Loaded {len(verses)} verses")
    print(verses[0])