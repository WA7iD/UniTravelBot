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

# --------------------- City Data ---------------------
city_data = {
    "Pyatigorsk": {
        "region": "North Caucasian Federal District",
        "fields": ["Medicine", "Pedagogy", "Economics"],
        "description": "Pyatigorsk — a place where cool resorts meet medical career prospects! 😎✨ Here you can dive into health and psychology while breathing fresh mountain air. Top universities + chill vibes = a great career start. 🚀",
        "universities": [
            {"name": "PGMU", "fields": ["Medicine", "Pharmacy", "Health"]},
            {"name": "PGTU", "fields": ["Economics", "Engineering", "Tech Startups"]}
        ]
    },
    "Stavropol": {
        "region": "North Caucasian Federal District",
        "fields": ["Medicine", "Pedagogy", "Law"],
        "description": "Stavropol — become not just a great lawyer, but also a leader in education and medicine! 🌱⚖️ Study and enjoy life here. Ecology, medical research, law — everything for growth. 💡",
        "universities": [
            {"name": "Stavropol State Agrarian University", "fields": ["Agronomy", "Tech", "Ecology"]},
            {"name": "Stavropol Pedagogical University", "fields": ["Pedagogy", "Social Sciences", "Management"]}
        ]
    },
    "Rostov-on-Don": {
        "region": "Southern Federal District",
        "fields": ["Medicine", "Pedagogy", "Sociology"],
        "description": "Rostov — not just a big southern city, but a vibrant metropolis! 🌞💥 You’ll find your niche in medicine, pedagogy, or sociology — with a splash of southern energy. Bonus: swim in rivers when exams aren’t near. 😉",
        "universities": [
            {"name": "SFU", "fields": ["Pedagogy", "Sociology", "Economics", "Business"]},
            {"name": "RostGMU", "fields": ["Medicine", "Biology", "Health"]}
        ]
    }
}

# --------------------- Logging ---------------------
logging.basicConfig(level=logging.INFO)

# --------------------- Env Vars ---------------------
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
PORT = int(os.environ.get("PORT", "8443"))
webhook_url = os.environ.get("WEBHOOK_URL")

if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not found in environment variables.")
if not webhook_url:
    raise ValueError("WEBHOOK_URL is not found in environment variables.")

# --------------------- Quiz States ---------------------
(QUESTION1, QUESTION2, QUESTION3, SELECT_REGION) = range(4)

# --------------------- User Data ---------------------
user_scores = {}
user_profiles = {}

# --------------------- Questions ---------------------
questions = [
    {
        "q": "What do you enjoy the most?",
        "options": [
            {"text": "Helping people", "field": "med"},
            {"text": "Creating apps", "field": "it"},
            {"text": "Teaching", "field": "soc"},
            {"text": "Running a business", "field": "biz"},
            {"text": "Designing things", "field": "art"},
        ]
    },
    {
        "q": "Which subject do you like best?",
        "options": [
            {"text": "Biology", "field": "med"},
            {"text": "Math", "field": "biz"},
            {"text": "Computer Science", "field": "it"},
            {"text": "Psychology", "field": "soc"},
            {"text": "Art", "field": "art"},
        ]
    },
    {
        "q": "What job sounds most exciting?",
        "options": [
            {"text": "Doctor", "field": "med"},
            {"text": "Entrepreneur", "field": "biz"},
            {"text": "Software Developer", "field": "it"},
            {"text": "Social Worker", "field": "soc"},
            {"text": "Artist", "field": "art"},
        ]
    },
    {
        "q": "Choose an activity you’d enjoy:",
        "options": [
            {"text": "Volunteering at hospitals", "field": "med"},
            {"text": "Building a website", "field": "it"},
            {"text": "Creating a lesson plan", "field": "soc"},
            {"text": "Launching a startup", "field": "biz"},
            {"text": "Sketching/drawing", "field": "art"},
        ]
    }
]

# --------------------- Helper Functions ---------------------
def handle_answer(text, user_id):
    try:
        score = int(text.strip())
        if score < 1 or score > 5:
            return
        field = questions[len([v for v in user_scores[user_id].values() if v > 0])]["options"][score - 1]["field"]
        user_scores[user_id][field] += 1
    except:
        pass

def get_top_profile(user_id):
    scores = user_scores.get(user_id)
    if not scores:
        return None
    return max(scores, key=scores.get)

# --------------------- Conversation Handlers ---------------------
async def send_greeting(update, user_id):
    greeting_text = (
        f"Hello, {update.effective_user.first_name}! 🎯 Ready to explore your future career and the right university city? Let's go!\n\n"
        "First, take a short quiz to find out which path fits you best!\n\n"
    )
    q = questions[0]
    message_text = (
        greeting_text +
        f"Question 1: {q['q']}\n" +
        "\n".join([f"{i+1} - {opt['text']}" for i, opt in enumerate(q['options'])])
    )
    await update.message.reply_text(message_text)
    return QUESTION1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_scores:
        user_scores[user_id] = {"med": 0, "art": 0, "biz": 0, "it": 0, "soc": 0}
    return await send_greeting(update, user_id)

async def question1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    handle_answer(update.message.text, update.effective_user.id)
    q = questions[1]
    await update.message.reply_text(
        f"Question 2: {q['q']}\n" + "\n".join([f"{i+1} - {opt['text']}" for i, opt in enumerate(q['options'])])
    )
    return QUESTION2

async def question2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    handle_answer(update.message.text, update.effective_user.id)
    q = questions[2]
    await update.message.reply_text(
        f"Question 3: {q['q']}\n" + "\n".join([f"{i+1} - {opt['text']}" for i, opt in enumerate(q['options'])])
    )
    return QUESTION3

async def question3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    handle_answer(update.message.text, update.effective_user.id)
    q = questions[3]
    await update.message.reply_text(
        f"Question 4: {q['q']}\n" + "\n".join([f"{i+1} - {opt['text']}" for i, opt in enumerate(q['options'])])
    )
    return SELECT_REGION

async def select_region(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selected_region = update.message.text
    user_id = update.effective_user.id
    profile = get_top_profile(user_id)

    if not profile:
        await update.message.reply_text("Couldn’t determine your profile. Please try again.")
        return ConversationHandler.END

    user_profiles[user_id] = profile
    await update.message.reply_text(
        "Now choose a federal district you’d like to study in:\nOptions:",
        reply_markup=ReplyKeyboardMarkup(
            [['Central', 'Volga'], ['Southern', 'North Caucasian']],
            one_time_keyboard=True, resize_keyboard=True
        )
    )
    return SELECT_REGION

async def handle_final_city_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selected_region = update.message.text
    user_id = update.effective_user.id
    profile = user_profiles.get(user_id)

    matching_cities = [
        city for city, info in city_data.items()
        if info["region"] == selected_region and profile in info["fields"]
    ]

    if matching_cities:
        reply = "Cities matching your profile in selected region:\n"
        for city in matching_cities:
            info = city_data[city]
            reply += f"\n{city}: {info['description']}\nUniversities: {', '.join([v['name'] for v in info['universities']])}\n"
        await update.message.reply_text(reply)
    else:
        await update.message.reply_text("Unfortunately, no matching cities found in this region.")

    return ConversationHandler.END

# --------------------- Run Bot ---------------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            QUESTION1: [MessageHandler(filters.TEXT & ~filters.COMMAND, question1)],
            QUESTION2: [MessageHandler(filters.TEXT & ~filters.COMMAND, question2)],
            QUESTION3: [MessageHandler(filters.TEXT & ~filters.COMMAND, question3)],
            SELECT_REGION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_final_city_response)],
        },
        fallbacks=[]
    )

    app.add_handler(conv_handler)
    app.run_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN, webhook_url=webhook_url)

if __name__ == "__main__":
    main()
