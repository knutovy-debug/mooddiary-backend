import os
import json
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY", "sk-b85cc66250d44ab387f095e498e23bf9"),
    base_url="https://api.deepseek.com"
)

def analyze_entry(text: str) -> dict:
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "Ты — эмпатичный психолог и друг. Внимательно прочитай текст пользователя. Дай развернутый, уникальный и полезный совет, который нельзя предугадать. Если текст грустный, поддержи; если радостный, порадуйся вместе с ним. Не повторяйся. Верни ТОЛЬКО JSON (без markdown) с полями: sentiment (positive/negative/neutral), stress_level (1-10), topics (массив строк), recommendation (строка с уникальным советом)."},
                {"role": "user", "content": text}
            ],
            response_format={"type": "json_object"}
        )
        # ВАЖНО: Превращаем строку из DeepSeek в словарь!
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Ошибка DeepSeek (проверь ключ): {e}")
        return {
            "sentiment": "neutral",
            "stress_level": 5,
            "topics": [],
            "recommendation": "Обратите внимание на свои мысли. Даже простые перерывы помогают восстановить баланс. Запишите, что вас беспокоит, и подумайте, какие шаги можно предпринять, чтобы это улучшить."
        }
