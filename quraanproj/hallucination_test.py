from groq import Groq

import os

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

question = "How many times does the word 'جبريل' (patience) appear in Surah Al-Baqarah specifically?"

response = client.chat.completions.create(

    model="llama-3.1-8b-instant",

    messages=[{"role": "user", "content": question}]

)

print(response.choices[0].message.content)
