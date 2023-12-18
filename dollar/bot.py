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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils import available_cities

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


@dp.message(Command('cities'))
async def show_available_cities(message: types.Message):
    available_cities_text = "\n".join(available_cities)
    response = f"Бот работает в следующих городах:\n{available_cities_text}"
    await message.answer(response)


@dp.message(lambda message: message.text == "Узнать курс по ЦБ")
async def action_check_cbr(message: types.Message):

    url = "https://quote.rbc.ru/ticker/72413?ysclid=loddzdqpq6156801105"
    driver = create_driver(url)
    elems = driver.find_element(By.CLASS_NAME, "chart__info__sum")
    dollar_rate = elems.text
    await message.reply(f"Курс доллара по ЦБ: {dollar_rate}")


@dp.message(lambda message: message.text in ["Купить $", "Продать $"])
async def action_ask_city(message: types.Message, state: FSMContext):

    await message.answer("В каком городе вы хотите купить или продать $?")
    await state.update_data(operation_type=message.text)
    await FormStates.waiting_for_city


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

    data_list = []

    if operation_type == "Купить $":

        while True:
            blocks = driver.find_elements(
                By.CSS_SELECTOR,
                'div[data-test="currency__rates-form__result-item"]')

            for block in blocks:
                bank_name = block.find_element(
                    By.CSS_SELECTOR,
                    'div[data-test="currenct--result-item--name"]').text
                exchange_rate_elements = block.find_elements(
                    By.CSS_SELECTOR,
                    'div[data-test="text"].Text__sc-j452t5-0.jzaqdw')
                exchange_rate = exchange_rate_elements[0].text if exchange_rate_elements else "0, ₽"

                search = bank_name.replace(' ', '')
                address = f'https://yandex.ru/maps/?text={search}'

                block_data = {
                    'bank_name': bank_name,
                    'exchange_rate': exchange_rate,
                    'address': address
                }

                data_list.append(block_data)

            try:
                show_more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        '//a[@data-role="button" and contains(@class, "Button__sc-16w8pak-2")]/span[text()="Показать еще"]')))
                driver.execute_script("arguments[0].click();",
                                      show_more_button)
            except Exception as e:
                print(f"Не удалось найти кнопку 'Показать еще'. \
                Завершаем цикл. Ошибка: {e}")
            break

        sorted_data_list = sorted(
            data_list,
            key=lambda x: float(x['exchange_rate'].replace('₽', '').replace(',', '.')))

        result = f"Курсы для покупки в городе {city}: {sorted_data_list}"

    elif operation_type == "Продать $":

        url = f'https://www.banki.ru/products/currency/cash/{slug_city}/?buttonId=3'
        driver = create_driver(url)

        while True:
            blocks = driver.find_elements(
                By.CSS_SELECTOR,
                'div[data-test="currency__rates-form__result-item"]')

            for block in blocks:
                bank_name = block.find_element(
                    By.CSS_SELECTOR,
                    'div[data-test="currenct--result-item--name"]').text
                exchange_rate_elements = block.find_elements(
                    By.CSS_SELECTOR,
                    'div[data-test="text"].Text__sc-j452t5-0.jzaqdw')
                exchange_rate = exchange_rate_elements[0].text if exchange_rate_elements else "200, ₽"

                search = bank_name.replace(' ', '')
                address = f'https://yandex.ru/maps/?text={search}'

                block_data = {
                    'bank_name': bank_name,
                    'exchange_rate': exchange_rate,
                    'address': address
                }

                data_list.append(block_data)

            try:
                show_more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        '//a[@data-role="button" and contains(@class, "Button__sc-16w8pak-2")]/span[text()="Показать еще"]')))
                driver.execute_script("arguments[0].click();",
                                      show_more_button)

            except Exception as e:
                print(f"Не удалось найти кнопку 'Показать еще'. \
                Завершаем цикл. Ошибка: {e}")
            break

        sorted_data_list = sorted(
            data_list,
            key=lambda x: float(x['exchange_rate'].replace('₽', '').replace(',', '.')), reverse=True)

        result = f"Курсы для покупки в городе {city}: {sorted_data_list}"

    else:
        result = "Неизвестная операция"

    await message.answer(result)
    await state.clear()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
