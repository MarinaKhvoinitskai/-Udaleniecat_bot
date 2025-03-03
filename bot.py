import logging
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import ChatMemberUpdated
from aiogram.filters import ChatMemberUpdatedFilter
from aiogram.enums import ChatMemberStatus

# Замените на ваш Telegram Bot API токен
TOKEN = "ВАШ_ТОКЕН_БОТА"
# URL API Афины (уточни в настройках Афины)
ATHENA_API_URL = "https://ru.app.athenachat.ai/api"

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
from aiogram import Router
dp = Router()

# Логирование
logging.basicConfig(level=logging.INFO)

### 🔹 Функция отправки сообщений в Афину ###
def send_to_athena(text):
    data = {"text": text}
    response = requests.post(ATHENA_API_URL, json=data)
    
    if response.status_code == 200:
        return response.json().get("response", "Ошибка AI")
    else:
        return "Ошибка при обращении к Афине"

### 🔹 Команда /start ###
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer("Привет! Я бот-модератор с AI. Отправь мне сообщение, и я обработаю его через Афину!")

### 🔹 Проверка новых пользователей (удаление ботов) ###
@dp.chat_member(ChatMemberUpdatedFilter())
async def check_new_member(event: ChatMemberUpdated):
    if event.new_chat_member.status == ChatMemberStatus.MEMBER:
        user = event.new_chat_member.user

        if user.is_bot:
            try:
                await bot.ban_chat_member(event.chat.id, user.id)
                await bot.send_message(event.chat.id, f"🤖 Бот @{user.username} был удален!")
                logging.info(f"Удален бот: @{user.username}")
            except Exception as e:
                logging.error(f"Ошибка при удалении бота @{user.username}: {e}")

### 🔹 Отправка сообщений в Афину ###
@dp.message()
async def process_message(message: types.Message):
    ai_response = send_to_athena(message.text)
    await message.answer(ai_response)

### 🔹 Запуск бота ###
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
