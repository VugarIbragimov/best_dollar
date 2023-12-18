# Используйте образ Python
FROM python:3.9

# Установите зависимости бота
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируйте все файлы вашего бота в контейнер
COPY . /app/


# Запустите ваш бот
CMD ["python", "bot.py"]