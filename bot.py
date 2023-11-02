from telegram.ext import Updater, CommandHandler
from selenium.webdriver.common.by import By
from telegram import ReplyKeyboardMarkup

from create_driver import create_driver

BOT_TOKEN = '6831828947:AAFEuMRVYVtCMTukSyAs0VWp9Rnzf-DHdpE'


# Функция, которая будет вызываться при команде /start
def start(update, context):

    buttons = ReplyKeyboardMarkup([['/getrate',
                                    '/get_dollar_rate']],
                                  resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text("Привет! Я бот, который \
                              возвращает курс доллара.",
                              reply_markup=buttons,
                              )


# Функция для получения курса доллара с веб-сайта
def get_dollar_rate(update, context,):
    url = "https://quote.rbc.ru/ticker/72413?ysclid=loddzdqpq6156801105"
    driver = create_driver(url)

    elements = driver.find_element(By.CLASS_NAME,
                                   "chart__info__sum")

    dollar_rate = elements.text

    # Close the driver
    driver.quit()

    update.message.reply_text(f'Курс доллара по ЦБ: {dollar_rate}')


def ratebanki(update, context):
    update.message.reply_text("Курс доллара по все банки.ру ...")


def main():
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("get_dollar_rate", ratebanki))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("getrate", get_dollar_rate,))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
