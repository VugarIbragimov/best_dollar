from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from create_driver import create_driver

url = 'https://www.banki.ru/products/currency/cash/moskva/?buttonId=2'
driver = create_driver(url)


async def process_data(driver, operation_type):
    data_list = []

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
        key=lambda x: float(x['exchange_rate'].replace('₽', '').replace(',', '.')),
        reverse=operation_type == "Продать $")

    return sorted_data_list


available_cities = [
    'Абакан', 'Альметьевск', 'Ангарск', 'Архангельск', 'Астрахань',
    'Балашиха', 'Барнаул', 'Белгород', 'Бийск', 'Благовещенск', 'Братск',
    'Брянск',
    'Великий Новгород', 'Владивосток', 'Владикавказ', 'Владимир', 'Волгоград',
    'Волжский', 'Вологда', 'Воронеж',
    'Дзержинск',
    'Екатеринбург',
    'Златоуст',
    'Иваново', 'Ижевск', 'Иркутск',
    'Йошкар-Ола',
    'Казань', 'Калининград', 'Калуга', 'Кемерово', 'Киров',
    'Комсомольск-на-Амуре', 'Кострома', 'Краснодар', 'Красноярск', 'Курган',
    'Курск',
    'Липецк',
    'Магнитогорск', 'Махачкала', 'Миасс', 'Москва', 'Мурманск', 'Мытищи',
    'Набережные Челны', 'Находка', 'Нижневартовск', 'Нижнекамск',
    'Нижний Новгород', 'Нижний Тагил', 'Новокузнецк', 'Новороссийск',
    'Новосибирск',
    'Одинцово', 'Омск', 'Орел', 'Оренбург',
    'Пенза', 'Пермь', 'Петрозаводск', 'Петропавловск-Камчатский', 'Подольск',
    'Псков', 'Пятигорск',
    'Ростов-на-Дону', 'Рязань',
    'Самара', 'Санкт-Петербург', 'Саранск', 'Саратов', 'Севастополь',
    'Симферополь', 'Смоленск', 'Сочи', 'Ставрополь', 'Старый Оскол',
    'Стерлитамак', 'Сургут', 'Сызрань', 'Сыктывкар',
    'Таганрог', 'Тамбов', 'Тверь', 'Тольятти', 'Томск', 'Тула', 'Тюмень',
    'Улан-Удэ', 'Ульяновск', 'Уфа',
    'Хабаровск', 'Химки',
    'Чебоксары', 'Челябинск', 'Череповец', 'Чита',
    'Южно-Сахалинск',
    'Якутск', 'Ярославль'
    'абакан', 'альметьевск', 'ангарск', 'архангельск', 'астрахань', 'балашиха',
    'барнаул', 'белгород', 'бийск', 'благовещенск', 'братск', 'брянск',
    'великий новгород', 'владивосток', 'владикавказ', 'владимир', 'волгоград',
    'волжский', 'вологда', 'воронеж', 'дзержинск', 'екатеринбург', 'златоуст',
    'иваново', 'ижевск', 'иркутск', 'йошкар-ола', 'казань', 'калининград',
    'калуга', 'кемерово', 'киров', 'комсомольск-на-амуре', 'кострома',
    'краснодар', 'красноярск', 'курган', 'курск', 'липецк', 'магнитогорск',
    'махачкала', 'миасс', 'москва', 'мурманск', 'мытищи', 'набережные челны',
    'находка', 'нижневартовск', 'нижнекамск', 'нижний новгород',
    'нижний тагил', 'новокузнецк', 'новороссийск', 'новосибирск', 'одинцово',
    'омск', 'орел', 'оренбург', 'пенза', 'пермь', 'петрозаводск',
    'петропавловск-камчатский', 'подольск', 'псков', 'пятигорск',
    'ростов-на-дону', 'рязань', 'самара', 'санкт-петербург', 'саранск',
    'саратов', 'севастополь', 'симферополь', 'смоленск', 'сочи',
    'ставрополь', 'старый оскол', 'стерлитамак', 'сургут', 'сызрань',
    'сыктывкар', 'таганрог', 'тамбов', 'тверь', 'тольятти', 'томск', 'тула',
    'тюмень', 'улан-удэ', 'ульяновск', 'уфа', 'хабаровск', 'химки',
    'чебоксары', 'челябинск', 'череповец', 'чита', 'южно-сахалинск',
    'якутск', 'ярославль']

# @dp.message()
# async def process_city(message: types.Message, state: FSMContext):
#     city = message.text
#     slug_city = slugify(city)

#     url = f'https://www.banki.ru/products/currency/cash/{slug_city}/?buttonId=2'
#     driver = create_driver(url)

#     data = await state.get_data()
#     operation_type = data.get('operation_type')

#     if operation_type not in ["Купить $", "Продать $"]:
#         await message.answer("Неизвестная операция")
#         await state.clear()
#         return

#     sorted_data_list = await process_data(driver, operation_type)

#     result = f"Курсы для {'покупки' if operation_type == 'Купить $' else 'продажи'} в городе {city}: {sorted_data_list}"
#     await message.answer(result)
#     await state.clear()
