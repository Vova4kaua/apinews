import asyncio
import logging
import threading
import requests

from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils.executor import start_polling
import uvicorn

# === НАСТРОЙКИ ===
BOT_TOKEN = "ТВОЙ_ТОКЕН_ТГ_БОТА"  # ВСТАВЬ сюда свой токен
APP_ENDPOINT = "https://myapp.onrender.com/api/news"  # Сюда отправлять данные

# === ЛОГИ ===
logging.basicConfig(level=logging.INFO)

# === ИНИЦИАЛИЗАЦИЯ ===
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
app = FastAPI()

# === ХЕНДЛЕР СООБЩЕНИЙ ИЗ ТЕЛЕГРАМ ===
@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_news(message: Message):
    news_data = {
        "chat_id": message.chat.id,
        "from_user": message.from_user.full_name if message.from_user else "unknown",
        "text": message.text
    }

    logging.info(f"[BOT] Получено сообщение: {news_data}")

    try:
        response = requests.post(APP_ENDPOINT, json=news_data)
        logging.info(f"[BOT] Отправлено в API ({response.status_code})")
    except Exception as e:
        logging.error(f"[BOT] Ошибка при отправке: {e}")

# === ПРОСТОЙ ЭНДПОИНТ ПРОВЕРКИ ===
@app.get("/")
def root():
    return {"status": "бот работает"}

# === ЭНДПОИНТ ДЛЯ ПОЛУЧЕНИЯ ДАННЫХ ИЗВНЕ ===
@app.post("/api/news")
async def receive_news(request: Request):
    data = await request.json()
    logging.info(f"[API] Получено извне: {data}")
    return {"status": "ок", "received": data}

# === ЗАПУСК БОТА В ОТДЕЛЬНОМ ПОТОКЕ ===
def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start_polling(dp, skip_updates=True)

# === ЗАПУСК ВСЕГО СЕРВЕРА ===
if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    uvicorn.run(app, host="0.0.0.0", port=10000)
