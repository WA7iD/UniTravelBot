from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

# Сюда вставь свой токен, который ты получишь у @BotFather
TOKEN = 'YOUR_BOT_TOKEN'

# Состояния диалога
START, QUESTION1, QUESTION2, QUESTION3, RESULT = range(5)

# Словарь для хранения результатов
user_scores = {"med": 0, "art": 0, "biz": 0, "it": 0, "soc": 0}

# Функция старта
def start(update: Update, context: CallbackContext) -> int:
    user_scores.update({"med": 0, "art": 0, "biz": 0, "it": 0, "soc": 0})
    update.message.reply_text(
        "Привет! 🎯 Пройди наш тест, чтобы узнать, какая профессия тебе подходит!\n\nНачнем?"
    )
    return QUESTION1

# Вопросы
def question1(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("🔥 Как проводишь свободное время?\n1. Читаю про здоровье\n2. Рисую/монтирую\n3. Искать, как заработать\n4. Разбираю гаджеты\n5. Общаюсь с людьми")
    return QUESTION2

def question2(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("💡 Твой любимый школьный предмет?\n1. Биология\n2. Литература/ИЗО\n3. Экономика\n4. Информатика\n5. Психология")
    return QUESTION3

def question3(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("📦 Что тебе важнее в работе?\n1. Помогать людям\n2. Творчество\n3. Финансовая независимость\n4. Решать задачи\n5. Общение с людьми")
    return RESULT

# Подсчёт результатов
def calculate_result(update: Update, context: CallbackContext) -> int:
    answer = update.message.text.lower()
    
    if "1" in answer:
        user_scores["med"] += 1
    elif "2" in answer:
        user_scores["art"] += 1
    elif "3" in answer:
        user_scores["biz"] += 1
    elif "4" in answer:
        user_scores["it"] += 1
    elif "5" in answer:
        user_scores["soc"] += 1

    # Подсчитываем, какой тип профессии тебе больше подходит
    top = max(user_scores, key=user_scores.get)

    if top == "med":
        result_text = "Ты подойдешь к профессиям в медицине, психологии или биотехнологиях."
    elif top == "art":
        result_text = "Ты креативный человек! Тебе подойдут профессии в дизайне, музыке, кино."
    elif top == "biz":
        result_text = "Ты ориентирован на результат и успех в бизнесе. Профессии в стартапах, маркетинге — твои!"
    elif top == "it":
        result_text = "Ты подходишь для работы в IT-сфере. Программирование, анализ данных — вот твоё!"
    elif top == "soc":
        result_text = "Тебе стоит попробовать себя в социальных профессиях, таких как педагогика, психология, HR."

    update.message.reply_text(result_text)
    return ConversationHandler.END

# Основная функция для старта бота
def main() -> None:
    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher

    # Создаем обработчик для команд и сообщений
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            QUESTION1: [MessageHandler(Filters.text & ~Filters.command, question1)],
            QUESTION2: [MessageHandler(Filters.text & ~Filters.command, question2)],
            QUESTION3: [MessageHandler(Filters.text & ~Filters.command, question3)],
            RESULT: [MessageHandler(Filters.text & ~Filters.command, calculate_result)],
        },
        fallbacks=[],
    )

    dispatcher.add_handler(conversation_handler)

    # Запускаем бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
