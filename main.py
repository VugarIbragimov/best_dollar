from selenium.webdriver.common.by import By
from create_driver import create_driver
# from selenium.common.exceptions import NoSuchElementException
# import time

url = "https://www.cbr.ru/"

driver = create_driver(url)  # создаем драйвер

# Найдем все элементы с указанным классом
elements = driver.find_elements(By.CLASS_NAME,
                                "col-md-2.col-xs-9._right.mono-num")

# Извлекаем текст из каждого элемента и сохраняем его в список
text = [element.text for element in elements]

print(text[3])
