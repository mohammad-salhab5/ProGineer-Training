from groq import Groq

import os

from retrieve import retrieve_verses

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a Quran assistant. Answer only using the verses provided below.

Always cite the surah name and ayah number for every verse you reference, in this format: (Surah Name, Ayah Number).

If the retrieved verses do not contain enough information to answer, say so clearly instead of guessing.

Do not provide religious rulings (fatwas) or interpretations beyond what is directly stated in the verses. 
If the question requires that kind of scholarly judgment, say so and recommend consulting a qualified scholar and 
allways Answer with arabic."""

def ask_quran_bot(question, top_k=5):

    verses = retrieve_verses(question, top_k=top_k)

    context = "\n".join([f"({v['reference']}): {v['text']}" for v in verses])

    user_message = f"""Retrieved verses:

{context}

Question: {question}"""

    response = client.chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=[

            {"role": "system", "content": SYSTEM_PROMPT},

            {"role": "user", "content": user_message}

        ]

    )

    return response.choices[0].message.content, verses

if __name__ == "__main__":

    answer, verses = ask_quran_bot("ما هي فضائل الصبر؟")

    print(answer)
