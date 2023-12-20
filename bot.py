import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from slugify import slugify

from create_driver import create_driver
from utils import available_cities, process_data

load_dotenv()
logging.basicConfig(level=logging.INFO)

load_dotenv()
tg_token = os.getenv('BOT_TOKEN')

bot = Bot(token=tg_token)
dp = Dispatcher(storage=MemoryStorage())

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Узнать курс по ЦБ"),
            KeyboardButton(text="Купить $"),
            KeyboardButton(text="Продать $"),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите дествие"
)


class FormStates:
    waiting_for_city = 'waiting_for_city'


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Чем могу быть полезен?", reply_markup=keyboard)


@dp.message(Command('cities'))
async def show_available_cities(message: types.Message):
    available_cities_text = "\n".join(available_cities)
    response = f"Бот работает в следующих городах:\n{available_cities_text}"
    await message.answer(response)


@dp.message(Command('help'))
async def show_avaiable_commands(message: types.Message):
    response = """Бот для получения курсов 💲 в различных городах:

1. Узнать курс 💲 по ЦБ: Бот предоставляет текущий курс доллара по Центральному Банку России.

2. Купить 💲: Выберите эту опцию, чтобы узнать лучшие курсы для покупки доллара в банках вашего города.

3. Продать 💲: Если вам нужно продать доллар, бот поможет найти банки с лучшими предложениями в вашем городе.

Инструкции по использованию:
- 👆Нажмите кнопки, описанные выше.👆
- Введите /start для начала общения с ботом и получения доступа к командам.
- Введите /cities для просмотра списка городов, в которых бот предоставляет информацию.🏙
- Введите /help для получения дополнительной информации о доступных командах.ℹ️
"""
    await message.answer(response)


@dp.message(lambda message: message.text == "Узнать курс по ЦБ")
async def action_check_cbr(message: types.Message):

    url = "https://quote.rbc.ru/ticker/72413?ysclid=loddzdqpq6156801105"
    driver = create_driver(url)
    try:
        elems = driver.find_element(By.CLASS_NAME, "chart__info__sum")
    except Exception as ex:
        print(f"Не удалось найти курс по ЦБ. Ошибка {ex}")
    dollar_rate = elems.text.replace('₽', '')
    await message.reply(f"Курс доллара по ЦБ: {dollar_rate} ₽")


@dp.message(lambda message: message.text in ["Купить $", "Продать $"])
async def action_ask_city(message: types.Message, state: FSMContext):

    await message.answer("В каком городе вы хотите купить или продать $?")
    await state.update_data(operation_type=message.text)
    return FormStates.waiting_for_city


@dp.message()
async def process_city(message: types.Message, state: FSMContext):

    city = message.text

    slug_city = slugify(city)
    if city not in available_cities:
        await message.answer('Извините, данный город не обслуживается')
        return

    url = f'https://www.banki.ru/products/currency/cash/{slug_city}/?buttonId=2'
    driver = create_driver(url)

    data = await state.get_data()
    operation_type = data.get('operation_type')

    if operation_type == "Купить $":

        sorted_data_list = await process_data(driver, operation_type)

        result = f"Курсы для покупки 💲 в городе {city.capitalize()}:\n\n"

        for bank_data in sorted_data_list:
            result += f"🏦Банк: {bank_data['bank_name']}\n🔄 Курс: {bank_data['exchange_rate']}\n📍 Адрес: {bank_data['address']}\n\n"

    elif operation_type == "Продать $":

        url = f'https://www.banki.ru/products/currency/cash/{slug_city}/?buttonId=3'
        driver = create_driver(url)

        sorted_data_list = await process_data(driver, operation_type)

        result = f"Курсы для продажи 💲 в городе {city.capitalize()}:\n\n"

        for bank_data in sorted_data_list:
            result += f"🏦Банк: {bank_data['bank_name']}\n 🔄Курс: {bank_data['exchange_rate']}\n📍 Адрес: {bank_data['address']}\n\n"

    else:
        result = "Неизвестная операция"

    await message.answer(result)
    await state.clear()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
