import os
import config
from pymongo import MongoClient

# Берем пароль из твоего конфига (где os.environ.get)
password = config.MONGO_URL

# Собираем строку. Буква f перед кавычками обязательна — она подставляет переменную
uri = f"mongodb+srv://Database:{password}@cluster0.ni6tpad.mongodb.net/?appName=Cluster0"

# Подключаемся
client = MongoClient(uri)
db = client.get_default_database() # Автоматически выберет базу из кластера
