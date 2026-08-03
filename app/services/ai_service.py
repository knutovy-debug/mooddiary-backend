import json
from openai import OpenAI

# Вставляем ключ напрямую для проверки
client = OpenAI(
    base_url="https://api.deepseek.com/v1",
    api_key="sk_6007c2b76c12c19c9644c02a7598103f6a6aed6d0fa86e45",  # ваш ключ
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
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        print(f"Ошибка AI: {e}")
        return {
            "sentiment": "neutral",
            "stress_level": 5,
            "topics": ["ошибка", "ai"],
            "recommendation": "Не удалось выполнить анализ. Попробуйте позже."
        }