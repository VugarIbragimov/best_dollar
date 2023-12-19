# Используем базовый образ Python
FROM python:3.8-slim

# Устанавливаем зависимости
RUN apt-get update && \
    apt-get install -y wget gnupg && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable

# Устанавливаем необходимые Python-зависимости
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы приложения
COPY . /app

# Запускаем бот
CMD ["python", "bot.py"]