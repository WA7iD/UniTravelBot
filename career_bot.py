import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ConversationHandler
)

# --------------------- City Data ---------------------
city_data = {
    "Pyatigorsk": {
        "region": "North Caucasian Federal District",
        "fields": ["med", "soc", "biz"],
        "description": "Pyatigorsk — a place where cool resorts meet medical career prospects! 😎✨ Here you can dive into health and psychology while breathing fresh mountain air. Top universities + chill vibes = a great career start. 🚀",
        "universities": [
            {"name": "PGMU", "fields": ["Medicine", "Pharmacy", "Health"]},
            {"name": "PGTU", "fields": ["Economics", "Engineering", "Tech Startups"]}
        ]
    },
    "Stavropol": {
        "region": "North Caucasian Federal District",
        "fields": ["med", "soc", "biz"],
        "description": "Stavropol — become not just a great lawyer, but also a leader in education and medicine! 🌱⚖️ Study and enjoy life here. Ecology, medical research, law — everything for growth. 💡",
        "universities": [
            {"name": "Stavropol State Agrarian University", "fields": ["Agronomy", "Tech", "Ecology"]},
            {"name": "Stavropol Pedagogical University", "fields": ["Pedagogy", "Social Sciences", "Management"]}
        ]
    },
    "Rostov-on-Don": {
        "region": "Southern Federal District",
        "fields": ["med", "soc", "biz"],
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
(QUESTION1, QUESTION2, QUESTION3, QUESTION4, SELECT_REGION, SELECT_CITY) = range(6)

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

def handle_answer(text, user_id, question_index):
    try:
        score = int(text.strip())
        if 1 <= score <= 5:
            field = questions[question_index]['options'][score - 1]['field']
            user_scores[user_id][field] += 1
    except:
        pass

def get_top_profile(user_id):
    scores = user_scores.get(user_id)
    if not scores:
        return None
    return max(scores, key=scores.get)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_scores[user_id] = {"med": 0, "art": 0, "biz": 0, "it": 0, "soc": 0}
    await update.message.reply_text(f"Hello, {update.effective_user.first_name}! 🎯 Ready to discover your future career path?\nLet's begin with a quick quiz!\n")
    return await send_question(update, 0)

async def send_question(update: Update, index):
    q = questions[index]
    text = f"Question {index + 1}: {q['q']}\n" + "\n".join([f"{i+1} - {opt['text']}" for i, opt in enumerate(q['options'])])
    await update.message.reply_text(text)
    return [QUESTION1, QUESTION2, QUESTION3, QUESTION4][index]

async def question1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    handle_answer(update.message.text, update.effective_user.id, 0)
    return await send_question(update, 1)

async def question2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    handle_answer(update.message.text, update.effective_user.id, 1)
    return await send_question(update, 2)

async def question3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    handle_answer(update.message.text, update.effective_user.id, 2)
    return await send_question(update, 3)

async def question4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    handle_answer(update.message.text, update.effective_user.id, 3)
    profile = get_top_profile(update.effective_user.id)
    user_profiles[update.effective_user.id] = profile

    messages = {
        "med": "You’re a natural fit for medicine, biology, or psychology 🧬",
        "it": "You’d thrive in tech, programming, and all things digital 💻",
        "soc": "You shine in education, communication, or social work 🧑‍🏫",
        "biz": "Business, leadership, and finance are your strong suits 📈",
        "art": "Your creativity belongs in art, design, or media 🎨"
    }

    await update.message.reply_text(messages.get(profile, "Interesting mix!"))

    keyboard = [[InlineKeyboardButton("Southern Federal District", callback_data="Southern Federal District")],
                [InlineKeyboardButton("North Caucasian Federal District", callback_data="North Caucasian Federal District")]]

    await update.message.reply_text(
        "Now let's choose a place where you want to study!\nYou can start with what is closer to you in spirit or simply interesting:\nFirstly, select a federal district:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return SELECT_REGION

async def select_region(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    region = query.data
    user_id = query.from_user.id
    profile = user_profiles[user_id]

    matching_cities = [city for city, info in city_data.items() if info['region'] == region and profile in info['fields']]

    buttons = [[InlineKeyboardButton(city, callback_data=f"CITY_{city}")] for city in matching_cities]
    await query.message.reply_text("We can offer you to get acquainted with the following cities:",
                                   reply_markup=InlineKeyboardMarkup(buttons))
    return SELECT_CITY

async def select_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    city = query.data.replace("CITY_", "")
    data = city_data.get(city)

    if data:
        text = f"{city}: {data['description']}\nUniversities: {', '.join([u['name'] for u in data['universities']])}"
        await query.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Click to find out more", callback_data="END", disabled=True)]
            ])
        )

    return ConversationHandler.END

async def fallback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please start with /start to begin the quiz.")

# --------------------- Run Bot ---------------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            QUESTION1: [MessageHandler(filters.TEXT & ~filters.COMMAND, question1)],
            QUESTION2: [MessageHandler(filters.TEXT & ~filters.COMMAND, question2)],
            QUESTION3: [MessageHandler(filters.TEXT & ~filters.COMMAND, question3)],
            QUESTION4: [MessageHandler(filters.TEXT & ~filters.COMMAND, question4)],
            SELECT_REGION: [CallbackQueryHandler(select_region)],
            SELECT_CITY: [CallbackQueryHandler(select_city)]
        },
        fallbacks=[MessageHandler(filters.ALL, fallback_handler)]
    )

    app.add_handler(conv_handler)
    app.run_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN, webhook_url=webhook_url)

if __name__ == "__main__":
    main()
