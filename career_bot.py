import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler
)

# Токен Telegram-бота (из переменной окружения)
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
PORT = int(os.environ.get('PORT', '8443'))
webhook_url = os.environ.get("WEBHOOK_URL")

# Проверка наличия токена и URL
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not found in environment variables.")

if not webhook_url:
    raise ValueError("WEBHOOK_URL is not found in environment variables.")

# Этапы теста
QUESTION1, QUESTION2, QUESTION3, QUESTION4 = range(4)

# Пользовательские данные
user_scores = {}

# Вопросы и ответы
questions = [
    {
        "q": "🔥 Как проводишь свободное время?",
        "options": [
            {"button": "Читаю про тело, здоровье, болезни (да, мне интересно)", "score": "med"},
            {"button": "Пишу, рисую, монтирую — люблю креатив", "score": "art"},
            {"button": "Ищу, как заработать на мемах", "score": "biz"},
            {"button": "Разбираю гаджеты или залипаю в код", "score": "it"},
            {"button": "Люблю помогать и разруливать чужие конфликты", "score": "soc"}
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

# Стартовая функция
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_scores[user_id] = {"med": 0, "art": 0, "biz": 0, "it": 0, "soc": 0}

    # Отправка первого вопроса
    await update.message.reply_text(
        f"Привет, {update.effective_user.first_name}! 🎯 Пройди короткий тест, чтобы узнать, какая профессия тебе подходит!\n\n"
        f"Вопрос 1: {questions[0]['q']}\n"
        f"1 — {questions[0]['options'][0]['text']}\n"
        f"2 — {questions[0]['options'][1]['text']}\n"
        f"3 — {questions[0]['options'][2]['text']}\n"
        f"4 — {questions[0]['options'][3]['text']}\n"
        f"5 — {questions[0]['options'][4]['text']}"
    )
    return QUESTION1

# Функции для обработки ответов
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

# Обработка ответов пользователя
def handle_answer(answer_text, user_id):
    answer_map = {
        "1": "med",
        "2": "art",
        "3": "biz",
        "4": "it",
        "5": "soc"
    }
    if answer_text in answer_map:
        user_scores[user_id][answer_map[answer_text]] += 1

# Функция для получения результата
def get_result(user_id):
    result_map = {
        "med": "👩‍⚕️ Тебе подойдёт медицина или психология! Ты заботлив(а), внимателен(на) и умеешь слушать. Профессии: врач, психолог, биотехнолог, нутрициолог",
        "art": "🎨 Ты — творец! У тебя развит вкус и креатив. Подойдут профессии: дизайнер, режиссёр, копирайтер, маркетолог",
        "biz": "📈 Будущий предприниматель! Ты про деньги, идеи и эффективность. Твои сферы: бизнес, управление, реклама, стартапы",
        "it": "💻 Айтишник в душе! Ты точно найдёшь себя в программировании, аналитике или разработке игр",
        "soc": "🗣️ Коммуникатор и лидер)) Ты умеешь быть в центре команды. Педагогика, HR, менеджмент, соц. проекты — твоё поле"
    }
    scores = user_scores[user_id]
    top = max(scores, key=scores.get)
    return result_map[top]

# Главная функция
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            QUESTION1: [MessageHandler(filters.TEXT & ~filters.COMMAND, question1)],
            QUESTION2: [MessageHandler(filters.TEXT & ~filters.COMMAND, question2)],
            QUESTION3: [MessageHandler(filters.TEXT & ~filters.COMMAND, question3)],
            QUESTION4: [MessageHandler(filters.TEXT & ~filters.COMMAND, question4)],
        },
        fallbacks=[],
    )

    app.add_handler(conv_handler)

    # Запуск через webhook (для Render)
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=webhook_url
    )

if __name__ == '__main__':
    main()
