import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Инициализация клиента DeepSeek
client = OpenAI(
    base_url="https://api.deepseek.com/v1",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)

SYSTEM_PROMPT = """
Ты — психологический аналитик. Проанализируй текст пользователя и верни строго JSON:
{
    "sentiment": "positive" | "neutral" | "negative",
    "topics": ["список", "ключевых", "тем"],
    "stress_level": число от 1 до 10,
    "recommendation": "короткая рекомендация (до 100 символов)"
}
"""

async def analyze_entry(text: str) -> dict:
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print("DeepSeek error:", e)
        return {
            "sentiment": "neutral",
            "stress_level": 5,
            "topics": ["ошибка"],
            "recommendation": "Не удалось выполнить анализ. Проверьте ключ или интернет."
        }