import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler
)

# Структура данных по городам
city_data = {
    "Пятигорск": {
        "округ": "СКФО",
        "направления": ["Медицина", "Педагогика", "Экономика"],
        "описание": "Пятигорск — место, где встречаются крутые курорты и перспективы в медицине! 😎✨ Здесь ты не только разберешься в здоровье и психологии, но и сможешь вдохнуть свежий горный воздух, отрываясь от рутины. Серьезные вузы + кайфовая атмосфера = удачный старт для твоей карьеры. 🚀",
        "вузы": [
            {"название": "ПГМУ", "направления": ["Медицина", "Фармацевтика", "Здоровье"]},
            {"название": "ПГТУ", "направления": ["Экономика", "Инженерия", "Техностартапы"]}
        ]
    },
    # Добавьте другие города, как выше
}

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Токен и настройки вебхука
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
PORT = int(os.environ.get('PORT', '8443'))
webhook_url = os.environ.get("WEBHOOK_URL")

if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not found in environment variables.")

if not webhook_url:
    raise ValueError("WEBHOOK_URL is not found in environment variables.")

# Этапы теста
(QUESTION1, QUESTION2, QUESTION3, SELECT_REGION) = range(4)

# Данные пользователя
user_scores = {}
user_profiles = {}

# Приветствие
async def send_greeting(update, user_id):
    try:
        greeting_text = (
            f"Привет, {update.effective_user.first_name}! 🎯 Думал(а) о ВУЗе, в который будешь поступать,"
            "а с городом решил(а)? Давай, мы тебя быстренько соориентируем 😉\n\n"
            "Пройди для начала короткий тест, чтобы узнать, кем ты можешь быть во взрослом мире!\n\n"
        )

        message_text = (
            greeting_text +
            f"Вопрос 1: {questions[0]['q']}\n"
            f"1 — {questions[0]['options'][0]['text']}\n"
            f"2 — {questions[0]['options'][1]['text']}\n"
            f"3 — {questions[0]['options'][2]['text']}\n"
            f"4 — {questions[0]['options'][3]['text']}\n"
            f"5 — {questions[0]['options'][4]['text']}"
        )

        await update.message.reply_text(message_text)
        return QUESTION1
    except Exception as e:
        logging.error(f"Ошибка при отправке приветствия: {e}")
        raise

# 🔹 Функция стартовой команды
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Инициализируем счётчики, если пользователь новый
    if user_id not in user_scores:
        user_scores[user_id] = {
            "med": 0,
            "art": 0,
            "biz": 0,
            "it": 0,
            "soc": 0
        }

    return await send_greeting(update, user_id)

# 🔹 Вопросы
async def question1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    handle_answer(update.message.text, update.effective_user.id)
    await update.message.reply_text(
        f"Вопрос 2: {questions[1]['q']}\n"
        f"1 — {questions[1]['options'][0]['text']}\n"
        f"2 — {questions[1]['options'][1]['text']}\n"
        f"3 — {questions[1]['options'][2]['text']}\n"
        f"4 — {questions[1]['options'][3]['text']}\n"
        f"5 — {questions[1]['options'][4]['text']}"
    )
    return QUESTION2

async def question2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    handle_answer(update.message.text, update.effective_user.id)
    await update.message.reply_text(
        f"Вопрос 3: {questions[2]['q']}\n"
        f"1 — {questions[2]['options'][0]['text']}\n"
        f"2 — {questions[2]['options'][1]['text']}\n"
        f"3 — {questions[2]['options'][2]['text']}\n"
        f"4 — {questions[2]['options'][3]['text']}\n"
        f"5 — {questions[2]['options'][4]['text']}"
    )
    return QUESTION3

async def question3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    handle_answer(update.message.text, update.effective_user.id)
    await update.message.reply_text(
        f"Вопрос 4: {questions[3]['q']}\n"
        f"1 — {questions[3]['options'][0]['text']}\n"
        f"2 — {questions[3]['options'][1]['text']}\n"
        f"3 — {questions[3]['options'][2]['text']}\n"
        f"4 — {questions[3]['options'][3]['text']}\n"
        f"5 — {questions[3]['options'][4]['text']}"
    )
    return SELECT_REGION

# 🔹 Функция для завершения теста и перехода к следующему этапу
async def handle_test_completion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    profile = get_top_profile(user_id)

    if not profile:
        await update.message.reply_text("Не удалось определить профиль. Попробуй пройти тест ещё раз.")
        return ConversationHandler.END

    user_profiles[user_id] = profile  # сохраняем профиль пользователя

    # Предлагаем выбрать регион
    await update.message.reply_text(
        "Теперь давай выберем регион, где ты хочешь учиться!\n"
        "Можешь начать с того, что тебе ближе по духу или просто интересен:"
    )

    reply_keyboard = [['ЦФО', 'ПФО'], ['ЮФО', 'СКФО']]
    await update.message.reply_text(
        "Выбери федеральный округ:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )

    return SELECT_REGION

# 🔹 Обработчик для выбора региона
async def select_region(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selected_region = update.message.text
    user_id = update.effective_user.id
    profile = user_profiles.get(user_id, 'it')  # Предположим, что профиль уже определён

    matching_cities = [
        city for city, info in city_data.items()
        if info["округ"] == selected_region and profile in info["направления"]
    ]

    if matching_cities:
        reply_text = "Города, подходящие тебе в выбранном округе:\n"
        for city in matching_cities:
            info = city_data[city]
            reply_text += f"\n{city}: {info['описание']}\nВузы: {', '.join([v['название'] for v in info['вузы']])}\n"
        await update.message.reply_text(reply_text)
    else:
        await update.message.reply_text("К сожалению, в этом округе нет подходящих городов по твоему профилю.")
    return ConversationHandler.END

# Запуск бота
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            QUESTION1: [MessageHandler(filters.TEXT & ~filters.COMMAND, question1)],
            QUESTION2: [MessageHandler(filters.TEXT & ~filters.COMMAND, question2)],
            QUESTION3: [MessageHandler(filters.TEXT & ~filters.COMMAND, question3)],
            SELECT_REGION: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_region)],
        },
        fallbacks=[],
    )

    app.add_handler(conv_handler)
    app.run_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN, webhook_url=webhook_url)

if __name__ == "__main__":
    main()
