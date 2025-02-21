# Используем официальный Python 3.10 образ
FROM python:3.10-slim

# Устанавливаем зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    libatlas-base-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
# Копируем код приложения в контейнер
COPY . /app
# Устанавливаем необходимые Python библиотеки
RUN pip install --no-cache-dir -r requirements.txt

# Открываем порт 8000 для приложения
EXPOSE 8000

# Запускаем сервер с помощью uvicorn
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]