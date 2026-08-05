import re

POSITIVE_WORDS = {'хорош', 'отличн', 'прекрасн', 'замечательн', 'рад', 'счастлив', 'люблю', 'нравит', 'удач', 'спокоен', 'легк'}
NEGATIVE_WORDS = {'плох', 'ужасн', 'нервн', 'тревожн', 'грустн', 'печальн', 'зл', 'раздраж', 'больн', 'страшн', 'боюсь', 'тяжел'}
STRESS_WORDS = {'стресс', 'пережив', 'волнуюсь', 'нерв', 'давл', 'устал', 'вымотан', 'спал'}

def get_topics(text: str) -> list:
    topics = []
    text_lower = text.lower()
    if re.search(r'работа|дел|начальник|коллег|проект|задач', text_lower):
        topics.append('работа')
    if re.search(r'друг|друз|семь|родн|отношени', text_lower):
        topics.append('отношения')
    if re.search(r'здоров|спорт|бег|ходьб|зарядк|сон|питани', text_lower):
        topics.append('здоровье')
    if re.search(r'день|утр|вечер|сегодня|завтра', text_lower):
        topics.append('день')
    if not topics:
        topics.append('общее')
    return topics

def analyze_entry(text: str) -> dict:
    text_lower = text.lower()
    words = set(re.findall(r'\w+', text_lower))

    pos_count = sum(1 for w in words if w in POSITIVE_WORDS or any(pos in w for pos in POSITIVE_WORDS))
    neg_count = sum(1 for w in words if w in NEGATIVE_WORDS or any(neg in w for neg in NEGATIVE_WORDS))

    if pos_count > neg_count:
        sentiment = 'positive'
    elif neg_count > pos_count:
        sentiment = 'negative'
    else:
        sentiment = 'neutral'

    stress_level = 5
    if any(w in words for w in STRESS_WORDS):
        stress_level += 2
    if neg_count > pos_count:
        stress_level += 2
    if len(text) > 200:
        stress_level += 1
    stress_level = max(1, min(10, stress_level))

    topics = get_topics(text)

    if stress_level >= 8:
        recommendation = "Вы чувствуете напряжение. Попробуйте сделать 5 глубоких вдохов или прогуляться."
    elif stress_level <= 3:
        recommendation = "У вас хорошее настроение! Поделитесь им с близкими."
    else:
        recommendation = "Спасибо, что поделились. Продолжайте заботиться о себе."

    return {
        "sentiment": sentiment,
        "stress_level": stress_level,
        "topics": topics,
        "recommendation": recommendation
    }