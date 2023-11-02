from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters
import logging

# Ваши команды и токен
BOT_TOKEN = '6831828947:AAFEuMRVYVtCMTukSyAs0VWp9Rnzf-DHdpE'


# Состояния разговора (conversation)
START, MENU = range(2)


# Создаем клавиатуру с кнопками
def create_keyboard():
    keyboard = [
        [InlineKeyboardButton("Команда 1", callback_data='command1')],
        [InlineKeyboardButton("Команда 2", callback_data='command2')],
        [InlineKeyboardButton("Команда 3", callback_data='command3')]
    ]
    return InlineKeyboardMarkup(keyboard)


# бработчик команды /start
def start(update, context):
    update.message.reply_text("Привет! Я бот, который возвращает курс доллара. Выберите команду:",
                              reply_markup=create_keyboard())
    return MENU


# Обработчик нажатия на кнопку
def button_handler(update, context):
    query = update.callback_query
    command = query.data

    if command == 'command1':
        update.callback_query.message.reply_text("Вы выбрали команду 1 и передали данные.")
    elif command == 'command2':
        update.callback_query.message.reply_text("Вы выбрали команду 2 и передали данные.")
    elif command == 'command3':
        update.callback_query.message.reply_text("Вы выбрали команду 3 и передали данные.")


# Основная функция
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Обработчик команды /start
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MENU: [CallbackQueryHandler(button_handler)]
        },
        fallbacks=[]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(logging.error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
