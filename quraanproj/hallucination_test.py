from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

question = "How many times does the word 'جبريل' (patience) appear in Surah Al-Baqarah specifically?"

response = client.chat.completions.create(

    model="llama-3.1-8b-instant",

    messages=[{"role": "user", "content": question}]

)

print(response.choices[0].message.content)
