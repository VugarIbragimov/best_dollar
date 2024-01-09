from selenium.webdriver.common.by import By
from functools import lru_cache
from cachetools import TTLCache


# Function for finding data for a city
async def process_data(driver, operation_type):
    data_list = []

    while True:
        try:
            blocks = driver.find_elements(
                By.CSS_SELECTOR,
                'div[data-test="currency__rates-form__result-item"]')
        except Exception as ex:
            print(f"Не удалось найти блоки с бвнквми. \
                  завершаем цикл. Ошибка: {ex}")

        for block in blocks:
            try:
                bank_name = block.find_element(
                    By.CSS_SELECTOR,
                    'div[data-test="currenct--result-item--name"]').text
            except Exception as ex:
                print(f"Не удалось найти название с банка. \
                      Завершаем цикл. Ошибка: {ex}")

            try:
                exchange_rate_elements = block.find_elements(
                    By.CSS_SELECTOR,
                    'div[data-test="text"].Text__sc-j452t5-0.jzaqdw')
            except Exception as ex:
                print(f"Не удалось найти курс $ банка. \
                      Завершаем цикл. Ошибка: {ex}")

            exchange_rate = exchange_rate_elements[0].text if exchange_rate_elements else "0, ₽"

            search = bank_name.replace(' ', '').replace('«', '')
            address = f'https://yandex.ru/maps/?text={search}'

            block_data = {
                'bank_name': bank_name,
                'exchange_rate': exchange_rate,
                'address': address
            }

            data_list.append(block_data)

        break

    sorted_data_list = sorted(
        data_list,
        key=lambda x: float(x['exchange_rate'].replace('₽', '').replace(',', '.').replace('—', '0')),
        reverse=operation_type == "Продать $")

    return sorted_data_list


MAX_CACHE_SIZE = 128
CACHE_TTL = 600

cache = TTLCache(maxsize=MAX_CACHE_SIZE, ttl=CACHE_TTL)


# decorator for functon
def cached_function():
    def decorator(func):
        @lru_cache(maxsize=MAX_CACHE_SIZE)
        def wrapper(*args, **kwargs):
            key = (args, frozenset(kwargs.items()))
            value = cache.get(key)
            if value is not None:
                return value
            result = func(*args, **kwargs)
            cache[key] = result
            return result
        return wrapper
    return decorator


# Array for the cities served
available_cities = [
    'Абакан', 'Барнаул', 'Белгород', 'Владивосток', 'Владикавказ', 'Владимир',
    'Волгоград', 'Вологда', 'Воронеж', 'Екатеринбург', 'Иваново', 'Ижевск',
    'Иркутск', 'Калининград', 'Калуга', 'Курган', 'Курск', 'Москва',
    'Мурманск', 'Новосибирск', 'Оренбург', 'Пенза', 'Петрозаводск', 'Псков',
    'Ростов-на-Дону', 'Самара', 'Санкт-Петербург', 'Саранск', 'Саратов',
    'Смоленск', 'Тамбов', 'Томск', 'Тула', 'Чита', 'абакан', 'барнаул',
    'белгород', 'владивосток', 'владикавказ', 'владимир', 'волгоград',
    'вологда', 'воронеж', 'екатеринбург', 'иваново', 'ижевск',
    'иркутск', 'калининград', 'курган', 'курск', 'москва', 'мурманск',
    'новосибирск', 'оренбург', 'пенза', 'петрозаводск', 'псков',
    'ростов-на-дону', 'самара', 'санкт-петербург', 'саранск', 'саратов',
    'смоленск', 'тамбов', 'томск', 'тула', 'чита']
