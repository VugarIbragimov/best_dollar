import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from create_driver import create_driver
from selenium.webdriver.common.by import By
from aiogram import F
from aiogram.fsm.context import FSMContext
# from aiogram.filters.
# from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.fsm.storage.memory import MemoryStorage


logging.basicConfig(level=logging.INFO)

bot = Bot(token="6831828947:AAFEuMRVYVtCMTukSyAs0VWp9Rnzf-DHdpE")
dp = Dispatcher(storage=MemoryStorage())


class FormStates:
    waiting_for_city = 'waiting_for_city'


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = [
        [
            types.KeyboardButton(text="Узнать курс $ по ЦБ"),
            types.KeyboardButton(text="Купить $ в моем городе"),
            types.KeyboardButton(text="Продать $ в моем городе")
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите дествие"
    )
    await message.answer("Чем могу быть полезен?", reply_markup=keyboard)


@dp.message(F.text.lower() == "узнать курс $ по цб")
async def return_rate(message: types.Message):
    url = "https://quote.rbc.ru/ticker/72413?ysclid=loddzdqpq6156801105"
    driver = create_driver(url)
    elems = driver.find_element(By.CLASS_NAME,
                                "chart__info__sum")
    dollar_rate = elems.text
    await message.reply(f"Курс по ЦБ: {dollar_rate}")


@dp.message(F.text.lower() == "купить $ в моем городе")
async def buy_dollar(message: types.Message):
    await message.reply("В каком горооде хотите узнать актуальные курсы для покупки?")
    await FormStates.waiting_for_city.set()


@dp.message(F.text.lower() == "продать $ в моем городе")
async def sell_dollar(message: types.Message):
    await message.reply("В каком горооде хотите узнать актуальные курсы для продажи?")
    await FormStates.waiting_for_city.set()


@dp.message()
async def process_city(message: types.Message, state: FSMContext):
    city = message.text
    await state.update_data(city=city)

    city_data = await state.get_data()
    city = city_data['city']
    if message.text.lower() == "купить $ в моем городе":
        url = 'https://www.banki.ru/products/currency/cash/usd/moskva/?buttonId=1&currencyId=840'
    elif message.text.lower() == "продать $ в моем городе":
        url = 'https://www.banki.ru/products/currency/cash/usd/yosshkar-ola/'  # Замените на фактический URL
    else:
        pass
    # url = 'https://www.banki.ru/products/currency/cash/usd/yosshkar-ola/'
    driver = create_driver(url)
    elems = driver.find_elements(By.CLASS_NAME, 'Text__sc-j452t5-0.jzaqdw')
    dollar_rates = [elem.text for elem in elems]
    # dollar_ratess = dollar_rates.sort()
    # await state.finish()

    await message.reply(
        f"Город {city} сохранен. Теперь можно обрабатывать запросы.{dollar_rates}")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
