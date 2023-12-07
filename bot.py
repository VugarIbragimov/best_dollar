import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command
from create_driver import create_driver
from selenium.webdriver.common.by import By
from slugify import slugify

logging.basicConfig(level=logging.INFO)

bot = Bot(token="6831828947:AAFEuMRVYVtCMTukSyAs0VWp9Rnzf-DHdpE")
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


@dp.message(lambda message: message.text == "Узнать курс по ЦБ")
async def action_check_cbr(message: types.Message):
    url = "https://quote.rbc.ru/ticker/72413?ysclid=loddzdqpq6156801105"
    driver = create_driver(url)
    elems = driver.find_element(By.CLASS_NAME,
                                "chart__info__sum")
    dollar_rate = elems.text
    await message.reply(f"Курс доллара по ЦБ: {dollar_rate}")


@dp.message(lambda message: message.text in ["Купить $", "Продать $"])
async def action_ask_city(message: types.Message, state: FSMContext):
    # Действия 2 и 3: Задаем вопрос о городе
    await message.answer("В каком городе вы хотите купить или продать $?")
    # Сохраняем тип операции в состоянии FSM
    await state.update_data(operation_type=message.text)
    # Переходим в состояние ожидания города
    await FormStates.waiting_for_city.set()


@dp.message()
async def process_city(message: types.Message, state: FSMContext):

    city = message.text
    slug_city = slugify(city)

    data = await state.get_data()
    operation_type = data.get('operation_type')

    if operation_type == "Купить $":

        url = f'https://www.banki.ru/products/currency/cash/{slug_city}/?buttonId=2'
        # f'https://www.banki.ru/products/currency/cash/{slug_city}/'
        driver = create_driver(url)
        elems = driver.find_elements(By.CLASS_NAME, 'Text__sc-j452t5-0.jzaqdw')
        dollar_rates = [float(elem.text.replace(',', '.').strip(' ₽')) for elem in elems if '—' not in elem.text]
        # if elem.text.replace(',', '.').strip(' ₽').lstrip('-').isdigit()
        sorted_dollar_rates = sorted(dollar_rates[::2])
        result = f"Курсы для покупки в городе {city}: {sorted_dollar_rates}"
    elif operation_type == "Продать $":

        url = f'https://www.banki.ru/products/currency/cash/{slug_city}/?buttonId=3'
        driver = create_driver(url)
        elems = driver.find_elements(By.CLASS_NAME, 'Text__sc-j452t5-0.jzaqdw')
        dollar_rates = [float(elem.text.replace(',', '.').strip(' ₽')) for elem in elems if '—' not in elem.text]

        sorted_dollar_rates = sorted(dollar_rates[::2], reverse=True)
        result = f"Курсы для продажи в городе {city}: {sorted_dollar_rates}"
    else:
        result = "Неизвестная операция"

    await message.answer(result)
    await state.clear()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
