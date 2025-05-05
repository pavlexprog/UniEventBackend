FROM python:3.11

# Установка рабочей директории
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё приложение
COPY . ./app

# Создаём директории media, avatars и events
RUN mkdir -p /app/media/avatars /app/media/events

# Команда запуска uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
