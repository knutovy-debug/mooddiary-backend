from app.services.rubert_service import analyze_entry as rubert_analyze

async def analyze_entry(text: str) -> dict:
    try:
        return await deepseek_analyze(text)
    except Exception as e:
        print("DeepSeek ошибка, используем RuBERT:", e)
        return rubert_analyze(text)