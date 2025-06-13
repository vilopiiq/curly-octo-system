import asyncio
import logging
import json
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties

# --- НАСТРОЙКИ ---
BOT_TOKEN = '7564273394:AAG9jDrhat3tY4X5E0NhJjkb-PQmKCIfI6Q'  # Your bot token

# !!! ВАЖНО !!!
# You mentioned you are using Vercel. Put your Vercel app URL here.
# It will look something like: https://your-project-name.vercel.app
WEB_APP_URL = "https://curly-octo-system-five.vercel.app/" 

SCORES_FILE = 'user_scores.json' # File to store user scores

# --- КОНЕЦ НАСТРОЕК ---


# Логирование для отладки
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
dp = Dispatcher()
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)

# --- ФУНКЦИИ ДЛЯ СОХРАНЕНИЯ ДАННЫХ ---

def load_scores():
    """Загружает очки пользователей из файла JSON."""
    try:
        with open(SCORES_FILE, 'r') as f:
            # Преобразуем ключи из строк обратно в int
            return {int(k): v for k, v in json.load(f).items()}
    except (FileNotFoundError, json.JSONDecodeError):
        # Если файл не найден или пуст/поврежден, возвращаем пустой словарь
        return {}

def save_scores(scores):
    """Сохраняет очки пользователей в файл JSON."""
    with open(SCORES_FILE, 'w') as f:
        json.dump(scores, f, indent=4)

# Загружаем очки при запуске бота
user_scores = load_scores()


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
    # Получаем счет пользователя из загруженных данных
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
            
            # *** ГЛАВНОЕ ИЗМЕНЕНИЕ: Сохраняем данные в файл ***
            save_scores(user_scores)

            await message.answer(
                f"Отличная работа! ✨\nТвой счет сохранен: <b>{score} AUR</b>"
            )
        else:
            await message.answer("Не удалось получить данные о счете.")

    except json.JSONDecodeError:
        await message.answer("Ошибка: неверный формат данных.")
    except Exception as e:
        logging.error(f"Error in web_app_data_handler: {e}")
        await message.answer(f"Произошла непредвиденная ошибка.")


# Главная функция для запуска бота
async def main():
    # Удаляем вебхук, если он был установлен ранее, чтобы избежать конфликтов
    await bot.delete_webhook(drop_pending_updates=True)
    # Запускаем polling (опрос)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.info("Starting bot...")
    asyncio.run(main())