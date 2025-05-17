from flask import Flask, request, jsonify, send_from_directory
import requests
import json
import logging
import os
from flask_cors import CORS
from trello import TrelloClient
from config import STATES, WAAPI_URL, WAAPI_TOKEN, WAAPI_INSTANCE_ID, TRELLO_API_KEY, TRELLO_API_TOKEN, TRELLO_BOARD_ID, TRELLO_LIST_ID

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Включаем CORS для всех маршрутов
CORS(app)

# Инициализация клиента Trello
trello_client = TrelloClient(
    api_key=TRELLO_API_KEY,
    api_secret=TRELLO_API_TOKEN
)

# Для отладки и мониторинга входящих запросов
@app.route('/', methods=['GET', 'POST'])
def index():
    """Простой индексный маршрут для проверки доступности сервера"""
    logger.info(f"Получен запрос на индексную страницу: {request.method}")
    
    # Добавляем HTML с инструкцией по обходу предупреждения ngrok
    html = """
    <html>
        <head>
            <title>WhatsApp Bot Server</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                .container { max-width: 800px; margin: 0 auto; }
                pre { background: #f4f4f4; padding: 10px; border-radius: 5px; }
                .note { background: #ffffcc; padding: 10px; border-radius: 5px; margin-top: 20px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>WhatsApp Bot Server is running!</h1>
                <p>Ваш сервер успешно запущен и готов обрабатывать запросы от waApi WhatsApp.</p>
                
                <div class="note">
                    <h3>Примечание по ngrok:</h3>
                    <p>Если вы видите предупреждение от ngrok, вы можете обойти его, используя следующий заголовок в своих запросах:</p>
                    <pre>ngrok-skip-browser-warning: true</pre>
                    <p>Для тестирования вебхука через Postman или другие инструменты добавьте этот заголовок.</p>
                </div>
                
                <h2>Endpoint для webhook:</h2>
                <pre>/webhook</pre>
            </div>
        </body>
    </html>
    """
    return html

# Хранение состояний пользователей и их данных
user_states = {}
user_data = {}

def get_user_state(phone_number):
    """Получение текущего состояния пользователя"""
    if (phone_number not in user_states):
        user_states[phone_number] = STATES['INITIAL']
        user_data[phone_number] = {}
    return user_states[phone_number]

def update_user_state(phone_number, new_state):
    """Обновление состояния пользователя"""
    user_states[phone_number] = new_state

def save_user_data(phone_number, key, value):
    """Сохранение данных пользователя"""
    if phone_number not in user_data:
        user_data[phone_number] = {}
    user_data[phone_number][key] = value

def send_to_trello(phone_number):
    """Отправка данных в Trello в виде карточки"""
    data = user_data[phone_number]
    
    # Формирование данных о клиенте и автомобиле
    client_info = f"""
Информация о клиенте:
ФИО: {data.get('name', '')}
Телефон: {phone_number}
Город: {data.get('city', '')}

Информация об автомобиле:
Марка: {data.get('car_brand', '')}
Год выпуска: {data.get('car_year', '')}
Пробег: {data.get('car_mileage', '')}
    """
    
    card_name = f'Заявка от {data.get("name", "Неизвестно")} ({data.get("car_brand", "")})'
    
    try:
        # Прямая отправка в Trello через API вместо использования библиотеки
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        query_params = {
            'key': TRELLO_API_KEY,
            'token': TRELLO_API_TOKEN,
            'name': card_name,
            'desc': client_info,
            'idList': TRELLO_LIST_ID,
            'pos': 'top'
        }
        
        trello_api_url = f"https://api.trello.com/1/cards"
        
        logger.info(f"Отправка запроса в Trello API: {trello_api_url}")
        response = requests.post(trello_api_url, params=query_params, headers=headers)
        
        if response.status_code == 200 or response.status_code == 201:
            card_data = response.json()
            logger.info(f"Карточка успешно создана в Trello, ID: {card_data.get('id')}")
            return {'result': True, 'card_id': card_data.get('id')}
        else:
            logger.error(f"Ошибка при создании карточки в Trello: {response.status_code} - {response.text}")
            
            # Запасной вариант - логирование данных локально
            logger.info(f"Локальное сохранение данных заявки: {card_name}")
            logger.info(client_info)
            
            # Можно сохранить в локальный файл для дальнейшего импорта
            try:
                with open('saved_applications.txt', 'a', encoding='utf-8') as f:
                    f.write(f"\n\n--- НОВАЯ ЗАЯВКА: {card_name} ---\n")
                    f.write(client_info)
                    f.write("\n--- КОНЕЦ ЗАЯВКИ ---\n")
                logger.info("Данные успешно сохранены в локальный файл")
            except Exception as write_error:
                logger.error(f"Ошибка при записи в файл: {write_error}")
            
            # Успешное завершение, даже если Trello недоступен
            return {'result': True, 'local_save': True}
            
    except Exception as e:
        logger.error(f"Ошибка при отправке данных в Trello: {e}", exc_info=True)
        
        # Запасной вариант - логирование данных локально
        logger.info(f"Локальное сохранение данных заявки: {card_name}")
        logger.info(client_info)
        
        # Можно сохранить в локальный файл для дальнейшего импорта
        try:
            with open('saved_applications.txt', 'a', encoding='utf-8') as f:
                f.write(f"\n\n--- НОВАЯ ЗАЯВКА: {card_name} ---\n")
                f.write(client_info)
                f.write("\n--- КОНЕЦ ЗАЯВКИ ---\n")
            logger.info("Данные успешно сохранены в локальный файл")
        except Exception as write_error:
            logger.error(f"Ошибка при записи в файл: {write_error}")
        
        # Успешное завершение, даже если Trello недоступен
        return {'result': True, 'local_save': True}

def send_whatsapp_message(phone_number, message):
    """Отправка сообщения через waApi WhatsApp"""
    url = f"{WAAPI_URL}/instances/{WAAPI_INSTANCE_ID}/client/action/send-message"
    
    # Удаляем '+' из номера телефона, если есть
    phone = phone_number.replace('+', '')
    
    # Формируем chatId в формате <phone_number>@c.us
    chat_id = f"{phone}@c.us"
    
    headers = {
        'Authorization': f'Bearer {WAAPI_TOKEN}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    payload = {
        "chatId": chat_id,
        "message": message,
        "previewLink": True
    }
    
    try:
        logger.info(f"Отправка сообщения через waApi: {payload}")
        response = requests.post(url, headers=headers, json=payload)
        logger.info(f"Ответ от waApi: {response.text}")
        
        # Проверка на успешную отправку
        if response.status_code == 200:
            try:
                response_data = response.json()
                if response_data.get('status') == 'success':
                    logger.info("Сообщение успешно отправлено")
                    return response_data
                else:
                    logger.error(f"Ошибка при отправке сообщения: {response_data}")
            except Exception as e:
                logger.error(f"Ошибка при обработке ответа JSON: {e}")
        else:
            logger.error(f"Ошибка HTTP при отправке сообщения: {response.status_code} - {response.text}")
        
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения через waApi: {e}", exc_info=True)
        return None

@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    """Основной обработчик сообщений WhatsApp"""
    # Логирование входящего запроса
    logger.info(f"Получен webhook запрос: {request.method}")
    
    # Проверка на пустой запрос
    if request.content_length == 0:
        logger.warning("Получен пустой запрос")
        return "OK", 200  # Возвращаем OK для пустых запросов
    
    # Получение данных из входящего сообщения
    if request.method == 'GET':
        logger.info("Получен GET запрос на webhook")
        return "Webhook is active", 200
    
    # Логирование данных формы и JSON
    if request.is_json:
        logger.info(f"JSON данные: {request.json}")
        data = request.json
    else:
        logger.info(f"Данные формы: {request.form}")
        data = request.form.to_dict()
    
    # Получение данных из сообщения waApi
    try:
        # Формат данных waApi.app для webhook
        if request.is_json:
            # Проверяем формат, который получен в текущем webhook
            if 'event' in data and data.get('event') == 'message' and 'data' in data:
                message_data = data.get('data', {}).get('message', {})
                
                # Извлекаем тело сообщения
                incoming_msg = message_data.get('body', '').strip()
                
                # Извлекаем номер отправителя, обычно в формате XXXXXXXXXXX@c.us
                sender_phone = message_data.get('from', '').split('@')[0] if '@' in message_data.get('from', '') else message_data.get('from', '')
                
                logger.info(f"Извлечены данные из webhook: сообщение='{incoming_msg}', отправитель={sender_phone}")
            elif 'messages' in data:
                # Старый формат для входящих сообщений
                message = data['messages'][0]
                if 'text' in message:
                    incoming_msg = message['text'].get('body', '').strip()
                elif 'caption' in message:
                    incoming_msg = message.get('caption', '').strip()
                else:
                    incoming_msg = message.get('body', '').strip()
                
                sender_phone = message.get('from', '').split('@')[0] if '@' in message.get('from', '') else message.get('from', '')
            else:
                # Для любых других форматов пытаемся извлечь нужные данные
                incoming_msg = ''
                sender_phone = ''
                
                # Рекурсивный поиск полей body и from в структуре JSON
                def extract_fields(obj, path=''):
                    nonlocal incoming_msg, sender_phone
                    if isinstance(obj, dict):
                        for key, value in obj.items():
                            if key == 'body' and isinstance(value, str) and not incoming_msg:
                                incoming_msg = value.strip()
                            elif key == 'from' and isinstance(value, str) and '@' in value and not sender_phone:
                                sender_phone = value.split('@')[0]
                            elif isinstance(value, (dict, list)):
                                extract_fields(value, path + '.' + key if path else key)
                    elif isinstance(obj, list):
                        for i, item in enumerate(obj):
                            extract_fields(item, f"{path}[{i}]")
                
                extract_fields(data)
                
                logger.info(f"Извлечены данные из альтернативного формата: сообщение='{incoming_msg}', отправитель={sender_phone}")
        else:
            # Для тестирования или альтернативных форматов
            incoming_msg = data.get('body', data.get('Body', '')).strip()
            sender_phone = data.get('from', data.get('From', '')).replace('whatsapp:', '')
            if '@' in sender_phone:
                sender_phone = sender_phone.split('@')[0]
    except Exception as e:
        logger.error(f"Ошибка при извлечении данных из входящего запроса: {e}", exc_info=True)
        return "OK", 200
    
    # Если нет данных в запросе, отправляем простой ответ
    if not incoming_msg or not sender_phone:
        logger.warning("Не найдены необходимые параметры в запросе")
        return "OK", 200
    
    logger.info(f"Сообщение: '{incoming_msg}' от {sender_phone}")
    
    # Получение текущего состояния пользователя
    current_state = get_user_state(sender_phone)
    
    # Подготовка ответа в зависимости от состояния
    response_message = ""
    
    # Обработка состояний и сообщений
    if current_state == STATES['INITIAL']:
        response_message = """RU: Здравствуйте, это компания Carso.kz!
Для обработки вашей заявки, пожалуйста, укажите ваше полное ФИО.
        
KZ: Сәлеметсіз бе, бұл Carso.kz компаниясы!
Өтінішіңізді өңдеу үшін толық аты-жөніңізді көрсетіңіз."""
        update_user_state(sender_phone, STATES['WAITING_FOR_NAME'])
    
    elif current_state == STATES['WAITING_FOR_NAME']:
        save_user_data(sender_phone, 'name', incoming_msg)
        response_message = """RU: Спасибо! Пожалуйста, укажите ваш город.
        
KZ: Рақмет! Енді қалаңызды көрсетіңіз."""
        update_user_state(sender_phone, STATES['WAITING_FOR_CITY'])
    
    elif current_state == STATES['WAITING_FOR_CITY']:
        save_user_data(sender_phone, 'city', incoming_msg)
        response_message = """RU: Отлично! Теперь, пожалуйста, укажите марку вашего автомобиля.
        
KZ: Тамаша! Енді көлігіңіздің маркасын жазыңыз."""
        update_user_state(sender_phone, STATES['WAITING_FOR_CAR_BRAND'])
    
    elif current_state == STATES['WAITING_FOR_CAR_BRAND']:
        save_user_data(sender_phone, 'car_brand', incoming_msg)
        response_message = """RU: Спасибо! Укажите, пожалуйста, год выпуска вашего автомобиля.
        
KZ: Рақмет! Көлігіңіздің шығарылған жылын көрсетіңіз."""
        update_user_state(sender_phone, STATES['WAITING_FOR_CAR_YEAR'])
    
    elif current_state == STATES['WAITING_FOR_CAR_YEAR']:
        save_user_data(sender_phone, 'car_year', incoming_msg)
        response_message = """RU: Почти готово! Осталось указать пробег вашего автомобиля (в км).
        
KZ: Бітейін деп қалды! Енді көлігіңіздің жүрісін (км) көрсетіңіз."""
        update_user_state(sender_phone, STATES['WAITING_FOR_CAR_MILEAGE'])
    
    elif current_state == STATES['WAITING_FOR_CAR_MILEAGE']:
        save_user_data(sender_phone, 'car_mileage', incoming_msg)
        
        # Отправка данных в Trello
        trello_response = send_to_trello(sender_phone)
        
        if trello_response and trello_response.get('result'):
            response_message = """RU: Спасибо за предоставленную информацию! Ваша заявка успешно отправлена. Наш менеджер свяжется с вами в ближайшее время.
            
KZ: Ақпаратыңыз үшін рахмет! Сіздің өтінішіңіз сәтті жіберілді. Менеджеріміз жақын арада сізбен хабарласады."""
        else:
            response_message = """RU: Спасибо за предоставленную информацию! Ваша заявка принята. Наш менеджер свяжется с вами в ближайшее время.
            
KZ: Ақпаратыңыз үшін рахмет! Өтінішіңіз қабылданды. Менеджеріміз жақын арада сізбен хабарласады."""
        
        update_user_state(sender_phone, STATES['COMPLETED'])
    
    elif current_state == STATES['COMPLETED']:
        response_message = """RU: Ваша заявка уже была отправлена. Если вы хотите создать новую заявку, напишите ‘Новая заявка’.
        
KZ: Сіздің өтінішіңіз бұрын жіберілген. Жаңа өтініш жасағыңыз келсе, ‘Жаңа өтініш’ деп жазыңыз."""
        
        if incoming_msg.lower() == 'новая заявка':
            # Сброс данных для новой заявки
            user_data[sender_phone] = {}
            update_user_state(sender_phone, STATES['INITIAL'])
            
            # Запуск новой заявки
            response_message = """RU: Здравствуйте! Для обработки вашей заявки, пожалуйста, укажите ваше полное ФИО.
            
KZ: Сәлеметсіз бе! Өтінішіңізді өңдеу үшін толық аты-жөніңізді көрсетіңіз."""
            update_user_state(sender_phone, STATES['WAITING_FOR_NAME'])
    
    # Отправка ответного сообщения через waApi
    if response_message:
        send_whatsapp_message(sender_phone, response_message)
    
    return "OK", 200

@app.route('/favicon.ico')
def favicon():
    """Обработчик для запросов фавиконки"""
    return "", 204  # Возвращаем пустой ответ со статусом 204 No Content

# Добавляем обработчик ошибок для отладки
@app.errorhandler(Exception)
def handle_error(e):
    logger.error(f"Произошла ошибка: {str(e)}", exc_info=True)
    return jsonify(error=str(e)), 500

if __name__ == '__main__':
    # Запуск на всех IP (0.0.0.0) чтобы принимать внешние запросы
    logger.info("Запуск сервера на 0.0.0.0:5050")
    app.run(debug=True, host='0.0.0.0', port=5050)