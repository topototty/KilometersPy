# Устанавливаем базовый образ Python
FROM python:3.10

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости проекта
COPY requirements.txt requirements.txt
# Устанавливаем зависимости
RUN apt-get install -y libcairo2 libpango-1.0-0 libgdk-pixbuf-2.0-0

RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в контейнер
COPY . .

# Открываем порт 8000
EXPOSE 8000

# Запускаем сервер разработки Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
