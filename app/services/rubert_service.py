import json
from transformers import pipeline

# Загружаем лёгкую модель для анализа тональности на русском
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="cointegrated/rubert-tiny-sentiment-balanced",
    device=-1  # -1 = CPU, 0 = GPU (если есть)
)

def analyze_entry(text: str) -> dict:
    try:
        result = sentiment_pipeline(text)[0]
        label = result['label']
        score = result['score']

        if label == 'positive':
            sentiment = 'positive'
            stress_level = 3
        elif label == 'negative':
            sentiment = 'negative'
            stress_level = 8
        else:
            sentiment = 'neutral'
            stress_level = 5

        # Простое выделение тем (можно улучшить)
        topics = []
        if 'работа' in text or 'дел' in text or 'начальник' in text:
            topics.append('работа')
        if 'день' in text or 'утро' in text or 'вечер' in text:
            topics.append('день')
        if 'друг' in text or 'семья' in text or 'родн' in text:
            topics.append('отношения')
        if not topics:
            topics.append('общее')

        if stress_level > 7:
            recommendation = "Вы чувствуете напряжение. Попробуйте сделать 5 глубоких вдохов или прогуляться."
        elif stress_level < 4:
            recommendation = "У вас хорошее настроение! Поделитесь им с близкими."
        else:
            recommendation = "Спасибо, что поделились. Продолжайте заботиться о себе."

        return {
            "sentiment": sentiment,
            "stress_level": stress_level,
            "topics": topics,
            "recommendation": recommendation
        }
    except Exception as e:
        print("RuBERT error:", e)
        return {
            "sentiment": "neutral",
            "stress_level": 5,
            "topics": ["ошибка"],
            "recommendation": "Не удалось выполнить анализ."
        }