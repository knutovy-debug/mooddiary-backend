from app.services.deepseek_service import analyze_entry as deepseek_analyze
from app.services.simpl_analyzer import analyze_entry as simple_analyze

async def analyze_entry(text: str) -> dict:
    try:
        return await deepseek_analyze(text)
    except Exception as e:
        print("DeepSeek error, using simple analyzer:", e)
        return simple_analyze(text)