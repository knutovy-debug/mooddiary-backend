import telebot
import requests

BOT_TOKEN = "8796483021:AAFTR7IwkRsnNLelncsVEer6Rt_r59JVvBM"
ADMIN_ID = "1177629279"
RAILWAY_URL = "https://web-production-e70f0c.up.railway.app"
ADMIN_SECRET = "ADMIN_SECRET_123" # Секретный ключ, который мы прописали в бэкенде

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    if str(message.chat.id) == ADMIN_ID:
        bot.reply_to(message, "Привет! Бот для подтверждения оплат работает.\nНапиши /activate <ID>, чтобы подтвердить оплату.")
    else:
        bot.reply_to(message, "Ты не админ.")

@bot.message_handler(commands=['activate'])
def activate(message):
    if str(message.chat.id) != ADMIN_ID:
        return
    try:
        user_id = int(message.text.split()[1])
        # Отправляем запрос на Railway
        url = f"{RAILWAY_URL}/api/v1/entries/admin/activate/{user_id}?secret={ADMIN_SECRET}"
        response = requests.post(url)
        
        if response.status_code == 200:
            bot.send_message(message.chat.id, f"✅ Подписка для пользователя {user_id} активирована!")
        else:
            bot.send_message(message.chat.id, f"❌ Ошибка: {response.text}")
    except:
        bot.send_message(message.chat.id, "Ошибка! Используй формат: /activate <ID>")

print("Бот запущен и слушает сообщения...")
bot.polling(none_stop=True)
