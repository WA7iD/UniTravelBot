import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackQueryHandler
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

# Стартовая функция
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_scores[user_id] = {"med": 0, "art": 0, "biz": 0, "it": 0, "soc": 0}

    # Отправка первого вопроса с кнопками
    keyboard = [
        [InlineKeyboardButton(option["text"], callback_data=option["score"]) for option in questions[0]["options"]]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Привет, {update.effective_user.first_name}! 🎯 Пройди короткий тест, чтобы узнать, какая профессия тебе подходит!\n\n"
        f"Вопрос 1: {questions[0]['q']}",
        reply_markup=reply_markup
    )
    return QUESTION1

# Функции для обработки ответов через кнопки
async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    score = query.data  # Получаем выбранное значение (score)
    user_scores[user_id][score] += 1

    # Переходим ко второму вопросу
    next_question = len(user_scores[user_id]) - 1
    if next_question < len(questions):
        # Каждая кнопка в своей строке
        keyboard = [
            [InlineKeyboardButton(option["text"], callback_data=option["score"])]
            for option in questions[next_question]["options"]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=f"Вопрос {next_question + 1}: {questions[next_question]['q']}",
            reply_markup=reply_markup
        )
    else:
        result = get_result(user_id)
        await query.edit_message_text(text=result)
        return ConversationHandler.END

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
            QUESTION1: [CallbackQueryHandler(handle_answer)],
            QUESTION2: [CallbackQueryHandler(handle_answer)],
            QUESTION3: [CallbackQueryHandler(handle_answer)],
            QUESTION4: [CallbackQueryHandler(handle_answer)],
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
