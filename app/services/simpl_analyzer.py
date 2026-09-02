import os
from openai import OpenAI

import os

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

def analyze_entry(text: str) -> dict:
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "Ты — дружелюбный психолог. Проанализируй дневник пользователя. Верни ТОЛЬКО JSON (без markdown). Поля: sentiment (positive/negative/neutral), stress_level (1-10), topics (массив строк), recommendation (строка)."},
                {"role": "user", "content": text}
            ],
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Ошибка DeepSeek: {e}")
        return {"sentiment": "neutral", "stress_level": 5, "topics": [], "recommendation": "Попробуйте расслабиться."}