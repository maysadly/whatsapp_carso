import os
from dotenv import load_dotenv

# Загрузка переменных из .env файла
load_dotenv()

# Конфигурация для waApi WhatsApp
WAAPI_URL = os.getenv('WAAPI_URL')
WAAPI_TOKEN = os.getenv('WAAPI_TOKEN')
WAAPI_INSTANCE_ID = os.getenv('WAAPI_INSTANCE_ID', '1')

# Конфигурация для Trello API
TRELLO_API_KEY = os.getenv('TRELLO_API_KEY')
TRELLO_API_TOKEN = os.getenv('TRELLO_API_TOKEN')
TRELLO_BOARD_ID = os.getenv('TRELLO_BOARD_ID')
TRELLO_LIST_ID = os.getenv('TRELLO_LIST_ID')

# Состояния диалога
STATES = {
    'INITIAL': 0,
    'WAITING_FOR_NAME': 1,
    'WAITING_FOR_CITY': 2,
    'WAITING_FOR_CAR_BRAND': 3,
    'WAITING_FOR_CAR_YEAR': 4,
    'WAITING_FOR_CAR_MILEAGE': 5,
    'COMPLETED': 6
}