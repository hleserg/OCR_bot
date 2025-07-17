"""
Конфигурационный файл для OCR телеграм бота
"""

import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Токен телеграм бота (читается из .env)
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Настройки логирования
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Проверка обязательных переменных
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения. Проверьте .env файл.")
