import os

from groq import Groq
from dotenv import load_dotenv


load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "user",
            "content": """
حوّل هذا السؤال إلى كلمات ومفاهيم للبحث في القرآن فقط:

ماهو الشيء الذي فقده موسى وكان فقدانه علامة على مكان لقائه بالخضر؟
"""
        }
    ],
    temperature=0
)

print(response)