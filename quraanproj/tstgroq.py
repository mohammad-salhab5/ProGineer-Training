import os

from groq import Groq

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)

response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {
            "role": "user",
            "content": "what is your name?"
        }
    ]
)

print(response.choices[0].message.content)