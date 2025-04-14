import os
import logging
from telegram import Update
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
    "Ставрополь": {
        "округ": "СКФО",
        "направления": ["Медицина", "Педагогика", "Юриспруденция"],
        "описание": "Ставрополь — здесь ты можешь стать не только крутым юристом, но и настоящим лидером в образовании и медицине! 🌱⚖️ Успеваешь и учиться, и наслаждаться жизнью. Экология, медицинские исследования, юрка — здесь есть все для развития. 💡",
        "вузы": [
            {"название": "Ставропольский ГАУ", "направления": ["Агрономия", "Технологии", "Экология"]},
            {"название": "Ставропольский Педагогический университет", "направления": ["Педагогика", "Социальные науки", "Менеджмент"]}
        ]
    },
    "Ростов-на-Дону": {
        "округ": "ЮФО",
        "направления": ["Медицина", "Педагогика", "Социология"],
        "описание": "Ростов — это не просто крупный южный город, это мегаполис с энергетикой, которая вдохновляет! 🌞💥 Здесь ты найдешь свою нишу в медицине, педагогике или социологии, а также погрузишься в атмосферу южного драйва. Бонус: возможность плавать в реках, пока не сессия. 😉",
        "вузы": [
            {"название": "ЮФУ", "направления": ["Педагогика", "Социология", "Экономика", "Бизнес"]},
            {"название": "РостГМУ", "направления": ["Медицина", "Биология", "Здоровье"]}
        ]
    }
}

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Токен и настройки вебхука
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
PORT = int(os.environ.get('PORT', '8443'))
webhook_url = os.environ.get("WEBHOOK_URL")

# Проверка переменных окружения
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not found in environment variables.")

if not webhook_url:
    raise ValueError("WEBHOOK_URL is not found in environment variables.")

# Этапы теста
(QUESTION1, QUESTION2, QUESTION3, SELECT_REGION, SELECT_CITY) = range(5)

# Данные пользователя
user_scores = {}

# Вопросы
questions = [
    {
        "q": "🔥 Как проводишь свободное время?",
        "options": [
            {"text": "Читаю про тело, здоровье, болезни (да, мне интересно)", "score": "med"},
            {"text": "Пишу, рисую, монтирую — люблю креатив", "score": "art"},
            {"text": "Ищу, как заработать на мемах", "score": "biz"},
            {"text": "Разбираю гаджеты или залипаю в код", "score": "it"},
            {"text": "Люблю помогать и разруливать чужие конфликты", "score": "soc"}
        ]
    },
    {
        "q": "💡 Твой любимый школьный предмет?",
        "options": [
            {"text": "Биология/Химия", "score": "med"},
            {"text": "Литература/ИЗО", "score": "art"},
            {"text": "Общество/Экономика", "score": "biz"},
            {"text": "Информатика/Математика", "score": "it"},
            {"text": "История/Психология", "score": "soc"}
        ]
    },
    {
        "q": "📦 Что тебе важнее в работе?",
        "options": [
            {"text": "Помогать людям и видеть результат", "score": "med"},
            {"text": "Творчество и самовыражение", "score": "art"},
            {"text": "Финансовая независимость", "score": "biz"},
            {"text": "Решать сложные задачи", "score": "it"},
            {"text": "Коммуникация и поддержка", "score": "soc"}
        ]
    },
    {
        "q": "🧠 Ты скорее...",
        "options": [
            {"text": "Аналитик, люблю разбираться в деталях", "score": "it"},
            {"text": "Эмпат, чувствую других", "score": "med"},
            {"text": "Креатор, всегда что-то придумываю", "score": "art"},
            {"text": "Организатор, люблю план и порядок", "score": "biz"},
            {"text": "Общительный, с кем угодно найду общий язык", "score": "soc"}
        ]
    }
]

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
    return QUESTION4

async def question4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    handle_answer(update.message.text, update.effective_user.id)
    result = get_result(update.effective_user.id)
    await update.message.reply_text(result)
    return ConversationHandler.END

# Обработка ответов
def handle_answer(answer_text, user_id):
    answer_map = {
        "1": "med",
        "2": "art",
        "3": "biz",
        "4": "it",
        "5": "soc"
    }

    if user_id not in user_scores:
        user_scores[user_id] = {
            "med": 0,
            "art": 0,
            "biz": 0,
            "it": 0,
            "soc": 0
        }

    if answer_text in answer_map:
        user_scores[user_id][answer_map[answer_text]] += 1

# Получение результата
def get_result(user_id):
    result_map = {
        "med": "👩‍⚕️ Тебе подойдёт медицина или психология!\nТы заботлив(а), внимателен(на) и умеешь слушать. Профессии: врач, психолог, биотехнолог, нутрициолог",
        "art": "🎨 Ты — творец!\nУ тебя развит вкус и креатив. Подойдут профессии: дизайнер, режиссёр, копирайтер, маркетолог",
        "biz": "📈 Будущий предприниматель!\nТы про деньги, идеи и эффективность. Твои сферы: бизнес, управление, реклама, стартапы",
        "it": "💻 Айтишник в душе!\nТы точно найдёшь себя в программировании, аналитике или разработке игр",
        "soc": "🗣️ Коммуникатор и лидер))\nТы умеешь быть в центре команды. Педагогика, HR, менеджмент, соц. проекты — твоё поле"
    }

    if user_id not in user_scores:
        return "Упс, похоже, у нас нет твоих данных. Пройди тест и попробуй снова!"

    scores = user_scores[user_id]
    if not scores:
        return "Ты не ответил(а) на вопросы. Пройди тест, чтобы получить результат!"

    top = max(scores, key=scores.get)
    return result_map.get(top, "Что-то пошло не так, попробуй ещё раз.")

# Функция, которая вызывается после завершения теста
async def handle_test_completion(update, context):
    user_id = update.message.chat.id
    
    # Здесь предполагается, что у тебя уже есть профиль пользователя
    user_profiles[user_id] = determined_profile

    # Теперь вызываем функцию для выбора региона
    await select_region(update, context)

# Функции для обработки выбора региона и города
async def select_region(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [['ЦФО', 'ПФО', 'ЮФО']]
    await update.message.reply_text(
        "Выбери федеральный округ:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return SELECT_CITY

async def select_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selected_region = update.message.text
    user_id = update.effective_user.id
    profile = user_profiles.get(user_id, 'it')  # Предположим, что профиль уже определён

    matching_cities = [
        city for city, info in city_data.items()
        if info["округ"] == selected_region and profile in info["направления"]
    ]

    if matching_cities:
        reply_text = "Города, подходящие тебе в выбранном округе:\n"
        for city in matching_cities:
            info = city_data[city]
            reply_text += f"\n{city}: {info['описание']}\nВузы: {', '.join(info['вузы'])}\n"
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
        QUESTION4: [MessageHandler(filters.TEXT & ~filters.COMMAND, question4)],
        SELECT_REGION: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_region)],
        SELECT_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_city)],
    },
    fallbacks=[CommandHandler('start', start)]
)

    app.add_handler(conv_handler)

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=webhook_url
    )

if __name__ == '__main__':
    main()
