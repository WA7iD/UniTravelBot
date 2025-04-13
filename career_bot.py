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

PORT = int(os.environ.get('PORT', '8443'))
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")  # исправляем на правильное название переменной

# Проверки на наличие токена и URL
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not found in environment variables.")
    
webhook_url = os.environ.get("WEBHOOK_URL")
if not webhook_url:
    raise ValueError("WEBHOOK_URL is not found in environment variables.")

# Этапы теста
QUESTION1, QUESTION2, QUESTION3 = range(3)

user_scores = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_scores[user_id] = {"med": 0, "art": 0, "biz": 0, "it": 0, "soc": 0}

    await update.message.reply_text(
        "Привет! 🎯 Пройди короткий тест, чтобы узнать, какая профессия тебе подходит!\n\n"
        "Вопрос 1: Как проводишь свободное время?\n"
        "1 — Читаю про здоровье\n"
        "2 — Рисую или монтирую\n"
        "3 — Думаю, как заработать\n"
        "4 — Разбираюсь с техникой\n"
        "5 — Общаюсь с людьми"
    )
    return QUESTION1

async def question1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    handle_answer(update.message.text, update.effective_user.id)
    await update.message.reply_text(
        "Вопрос 2: Любимый предмет в школе?\n"
        "1 — Биология\n"
        "2 — Литература / Искусство\n"
        "3 — Экономика\n"
        "4 — Информатика\n"
        "5 — Обществознание"
    )
    return QUESTION2

async def question2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    handle_answer(update.message.text, update.effective_user.id)
    await update.message.reply_text(
        "Вопрос 3: Что важнее в профессии?\n"
        "1 — Помогать людям\n"
        "2 — Креативность\n"
        "3 — Доход\n"
        "4 — Решать задачи\n"
        "5 — Общение"
    )
    return QUESTION3

async def question3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    handle_answer(update.message.text, update.effective_user.id)
    result = get_result(update.effective_user.id)
    await update.message.reply_text(result)
    return ConversationHandler.END

def handle_answer(text, user_id):
    if "1" in text:
        user_scores[user_id]["med"] += 1
    elif "2" in text:
        user_scores[user_id]["art"] += 1
    elif "3" in text:
        user_scores[user_id]["biz"] += 1
    elif "4" in text:
        user_scores[user_id]["it"] += 1
    elif "5" in text:
        user_scores[user_id]["soc"] += 1

def get_result(user_id):
    result_map = {
        "med": "Тебе подойдут профессии в медицине, биологии, психологии 🧬",
        "art": "Ты креативен! Попробуй себя в дизайне, искусстве, кино 🎨",
        "biz": "Ты предприимчив(а). Стартапы, маркетинг, финансы — твой путь 💼",
        "it": "Ты технарь! Программирование, AI, кибербезопасность — твоё 👾",
        "soc": "Ты душа компании! Образование, HR, социология — попробуй 🗣️"
    }
    scores = user_scores[user_id]
    top = max(scores, key=scores.get)
    return result_map[top]

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            QUESTION1: [MessageHandler(filters.TEXT & ~filters.COMMAND, question1)],
            QUESTION2: [MessageHandler(filters.TEXT & ~filters.COMMAND, question2)],
            QUESTION3: [MessageHandler(filters.TEXT & ~filters.COMMAND, question3)],
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
