import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from create_driver import create_driver
from selenium.webdriver.common.by import By

logging.basicConfig(level=logging.INFO)

bot = Bot(token="YOUR_BOT_TOKEN")
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

class FormStates:
    waiting_for_city = 'waiting_for_city'

@dp.message_handler(Command("start"))
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
        input_field_placeholder="Выберите действие"
    )
    await message.answer("Чем могу быть полезен?", reply_markup=keyboard)

@dp.message_handler(Text(equals="Купить $ в моем городе"))
async def buy_dollar(message: types.Message):
    await message.answer("В каком городе хотите узнать актуальные курсы для покупки?")
    await FormStates.waiting_for_city.set()

@dp.message_handler(state=FormStates.waiting_for_city)
async def process_city(message: types.Message, state: FSMContext):
    city = message.text
    await state.update_data(city=city)
    await state.finish()  # завершаем состояние

    # Здесь ты можешь передать город в Selenium и обработать запрос
    # Пример:
    # city_data = await state.get_data()
    # city = city_data['city']
    # выполнить логику с использованием Selenium...

    await message.reply(f"Город {city} сохранен. Теперь можно обрабатывать запросы.")

async def main():
    await dp.start_polling()

if name == "__main__":
    asyncio.run(main())
