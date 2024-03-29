# Используем базовый образ Python
FROM python:3.11

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файлы зависимостей и устанавливаем их
COPY /requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Копируем все остальные файлы в текущую рабочую директорию внутри контейнера
COPY . /app

# Указываем, какое приложение запускать при старте контейнера
CMD ["python", "./baum_ai_predict/pypy.py"]
