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

# Доступные языки
LANGUAGES = {
    'RU': 'ru',
    'KZ': 'kz'
}

# Состояния диалога для основных этапов
STATES = {
    'INITIAL': 0,
    'WAITING_FOR_LANGUAGE': 1,  # Новое состояние для выбора языка
    'WAITING_FOR_USER_TYPE': 2,
    'WAITING_FOR_NAME': 3,
    'WAITING_FOR_CITY': 4,
    'WAITING_FOR_CAR_BRAND': 5,
    'WAITING_FOR_CAR_YEAR': 6,
    'WAITING_FOR_CAR_MILEAGE': 7,
    'COMPLETED': 8
}

# Состояния для выбора режима работы
USER_TYPES = {
    'UNKNOWN': 0,       # Тип пользователя не определен
    'DEALERSHIP': 1,    # Автосалон (сотрудничество)
    'CLIENT': 2         # Клиент (регистрация гарантии)
}

# Состояния для автосалона
DEALERSHIP_STATES = {
    'WAITING_FOR_NAME': 10,
    'WAITING_FOR_ADDRESS': 11,
    'WAITING_FOR_COOPERATION': 12,  
    'WAITING_FOR_ID': 13,           # Запрос удостоверения
    'WAITING_FOR_TECHPASSPORT': 14, # Запрос техпаспорта
    'COMPLETED': 15
}

# Состояния для клиента
CLIENT_STATES = {
    'WAITING_FOR_CAR_NUMBER': 20,
    'WAITING_FOR_CITY': 21,
    'WAITING_FOR_MILEAGE': 22,
    'WAITING_FOR_ID': 23,           # Запрос удостоверения
    'WAITING_FOR_TECHPASSPORT': 24, # Запрос техпаспорта
    'COMPLETED': 25
}

# Тексты на разных языках
MESSAGES = {
    'ru': {
        # Выбор языка
        'choose_language': 'Добрый день, это компания Carso.kz!\nВыберите язык / Тілді таңдаңыз:\n1️⃣ Русский\n2️⃣ Қазақша',
        'invalid_language': 'Пожалуйста, выберите язык (введите 1 или 2):\n1️⃣ Русский\n2️⃣ Қазақша',
        
        # Выбор типа пользователя
        'select_user_type': 'Здравствуйте! Пожалуйста, выберите категорию:\n1️⃣ Автосалон\n2️⃣ Клиент',
        'invalid_user_type': 'Пожалуйста, выберите правильную категорию (введите 1 или 2):\n1️⃣ Автосалон\n2️⃣ Клиент',
        
        # Общие фразы
        'thanks': 'Спасибо!',
        
        # Для автосалона
        'dealership_name': 'Пожалуйста, укажите название вашего автосалона.',
        'dealership_address': 'Пожалуйста, укажите адрес вашего автосалона.',
        'dealership_cooperation': 'Отлично! Уже сотрудничаете с нами?\n1️⃣ Да\n2️⃣ Нет',
        'dealership_id': 'Спасибо! Пожалуйста, отправьте фото вашего удостоверения личности.',
        'dealership_techpassport': 'Теперь, пожалуйста, отправьте фото техпаспорта.',
        
        # Для клиента
        'client_car_number': 'Пожалуйста, укажите номер вашего автомобиля.',
        'client_city': 'Спасибо! Пожалуйста, укажите ваш город.',
        'client_mileage': 'Отлично! Пожалуйста, укажите пробег вашего автомобиля (в км).',
        'client_id': 'Спасибо! Пожалуйста, отправьте фото вашего удостоверения личности.',
        'client_techpassport': 'Теперь, пожалуйста, отправьте фото техпаспорта.',
        
        # Завершение
        'request_complete': 'Спасибо за предоставленную информацию! Ваша заявка успешно отправлена. Наш менеджер свяжется с вами в ближайшее время.',
        'new_request': 'Если хотите создать новую заявку, напишите "Новая заявка" или цифру 9️⃣.'
    },
    'kz': {
        # Выбор языка
        'choose_language': 'Добрый день, это компания Carso.kz!\nВыберите язык / Тілді таңдаңыз:\n1️⃣ Русский\n2️⃣ Қазақша',
        'invalid_language': 'Тілді таңдаңыз (1 немесе 2 енгізіңіз):\n1️⃣ Русский\n2️⃣ Қазақша',
        
        # Выбор типа пользователя
        'select_user_type': 'Сәлеметсіз бе! Санатты таңдаңыз:\n1️⃣ Автосалон\n2️⃣ Клиент',
        'invalid_user_type': 'Дұрыс санатты таңдаңыз (1 немесе 2 енгізіңіз):\n1️⃣ Автосалон\n2️⃣ Клиент',
        
        # Общие фразы
        'thanks': 'Рахмет!',
        
        # Для автосалона
        'dealership_name': 'Автосалоныңыздың атауын көрсетіңіз.',
        'dealership_address': 'Автосалоныңыздың мекенжайын көрсетіңіз.',
        'dealership_cooperation': 'Тамаша! Бізбен бұрыннан ынтымақтасасыз ба?\n1️⃣ Иә\n2️⃣ Жоқ',
        'dealership_id': 'Рахмет! Жеке куәлігіңіздің суретін жіберіңіз.',
        'dealership_techpassport': 'Енді көлік құжаттарының суретін жіберіңіз.',
        
        # Для клиента
        'client_car_number': 'Көлігіңіздің нөмірін көрсетіңіз.',
        'client_city': 'Рахмет! Қалаңызды көрсетіңіз.',
        'client_mileage': 'Тамаша! Көлігіңіздің жүрген жолын көрсетіңіз (км).',
        'client_id': 'Рахмет! Жеке куәлігіңіздің суретін жіберіңіз.',
        'client_techpassport': 'Енді көлік құжаттарының суретін жіберіңіз.',
        
        # Завершение
        'request_complete': 'Ақпарат үшін рахмет! Сіздің өтініміңіз сәтті жіберілді. Менеджер жақын арада сізбен байланысады.',
        'new_request': 'Жаңа өтінім жасағыңыз келсе, "Жаңа өтінім" деп жазыңыз немесе 9️⃣ санын енгізіңіз.'
    }
}