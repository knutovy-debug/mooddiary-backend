import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("sk-b85cc66250d44ab387f095e498e23bf9"), base_url="https://api.deepseek.com")

def analyze_entry(text: str) -> dict:
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "system", "content": "Ты — дружелюбный психолог. Проанализируй дневник пользователя. Верни ТОЛЬКО JSON. Поля: sentiment (positive/negative/neutral), stress_level (1-10), topics (массив строк), recommendation (строка)."}, {"role": "user", "content": text}],
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Ошибка DeepSeek: {e}")
        return {"sentiment": "neutral", "stress_level": 5, "topics": [], "recommendation": "Попробуйте расслабиться."}
