# Используем официальный образ Python 3.13 (slim-версия)
FROM python:3.13-slim

# Отключаем запись .pyc файлов и буферизацию вывода
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Задаем рабочую директорию внутри контейнера
WORKDIR /app

# Обновляем список пакетов и устанавливаем необходимые зависимости:
# build-essential и gcc — для сборки C-расширений
# libpq-dev — для сборки psycopg2
# zlib1g-dev — для поддержки zlib (Pillow)
# libjpeg-dev — для поддержки JPEG (Pillow)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    zlib1g-dev \
    libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей
COPY requirements.txt .

# Обновляем pip и устанавливаем Python-зависимости
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Копируем исходный код проекта в контейнер
COPY src .
# Копируем entrypoint-скрипт и даем ему права на выполнение
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Открываем порт 8000
EXPOSE 8000

# Используем entrypoint-скрипт для компиляции переводов и запуска приложения
ENTRYPOINT ["/entrypoint.sh"]