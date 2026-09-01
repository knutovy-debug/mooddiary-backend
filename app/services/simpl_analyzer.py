import os
from openai import OpenAI

# Подключаем DeepSeek (он поддерживает OpenAI SDK)
client = OpenAI(
    api_key=os.getenv("sk-b85cc66250d44ab387f095e498e23bf9"),
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
        # Фолбэк: если DeepSeek не отвечает, возвращаем простой результат
        return {"sentiment": "neutral", "stress_level": 5, "topics": [], "recommendation": "Попробуйте расслабиться."}