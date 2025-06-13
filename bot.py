import asyncio
import logging
import json
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.web_app_info import WebAppInfo

# --- НАСТРОЙКИ ---
# Вставьте сюда токен вашего бота
BOT_TOKEN = "YOUR_BOT_TOKEN"

# URL вашего веб-приложения (важный шаг, см. инструкцию ниже)
WEB_APP_URL = "YOUR_WEB_APP_URL" 

# --- КОНЕЦ НАСТРОЕК ---


# Логирование для отладки
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

# Простое "хранилище" для очков пользователей (в реальном приложении нужна БД)
user_scores = {}

# Обработчик команды /start
@dp.message(CommandStart())
async def command_start(message: Message):
    # Создаем кнопку, которая открывает Web App
    web_app_button = KeyboardButton(
        text="✨ Открыть AURA Clicker",
        web_app=WebAppInfo(url=WEB_APP_URL)
    )
    # Создаем клавиатуру с этой кнопкой
    reply_keyboard = ReplyKeyboardMarkup(
        keyboard=[[web_app_button]],
        resize_keyboard=True
    )
    
    user_id = message.from_user.id
    current_score = user_scores.get(user_id, 0)

    await message.answer(
        f"Привет, <b>{message.from_user.first_name}</b>!\n\n"
        "Добро пожаловать в <b>AURA Clicker</b>.\n"
        "Ваша цель — кликать на монету и накапливать <b>AURA</b>.\n\n"
        f"Твой текущий баланс: <b>{current_score} AUR</b>\n\n"
        "Нажми кнопку ниже, чтобы начать!",
        reply_markup=reply_keyboard
    )

# Обработчик данных, полученных из Web App
@dp.message(F.web_app_data)
async def web_app_data_handler(message: Message):
    try:
        # Данные приходят в виде строки JSON, парсим их
        data = json.loads(message.web_app_data.data)
        score = data.get('score')
        
        if score is not None:
            user_id = message.from_user.id
            user_scores[user_id] = score
            
            await message.answer(
                f"Отличная работа! ✨\nТвой счет сохранен: <b>{score} AUR</b>"
            )
        else:
            await message.answer("Не удалось получить данные о счете.")
            
    except json.JSONDecodeError:
        await message.answer("Ошибка: неверный формат данных.")
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")


# Главная функция для запуска бота
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())