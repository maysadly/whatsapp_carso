import logging
import os
import time
from trello import TrelloClient
from whatsapp_chatbot_python import GreenAPIBot, Notification
from config import (STATES, GREEN_API_ID_INSTANCE, GREEN_API_API_TOKEN, TRELLO_API_KEY, 
                   TRELLO_API_TOKEN, TRELLO_BOARD_ID, TRELLO_LIST_ID, USER_TYPES, 
                   DEALERSHIP_STATES, CLIENT_STATES, LANGUAGES, MESSAGES)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация клиента Trello
trello_client = TrelloClient(
    api_key=TRELLO_API_KEY,
    api_secret=TRELLO_API_TOKEN
)

# Инициализация бота Green API
bot = GreenAPIBot(
    GREEN_API_ID_INSTANCE,
    GREEN_API_API_TOKEN
)

# Хранение состояний пользователей и их данных
user_states = {}
user_data = {}
user_types = {}  # Хранение типа пользователя: автосалон или клиент
user_languages = {}  # Хранение выбранного языка пользователя
processed_messages = {}  # Для отслеживания обработанных сообщений

def get_user_state(phone_number):
    """Получение текущего состояния пользователя"""
    if (phone_number not in user_states):
        user_states[phone_number] = STATES['INITIAL']  # Начинаем с выбора языка
        user_data[phone_number] = {}
        user_types[phone_number] = USER_TYPES['UNKNOWN']
        user_languages[phone_number] = LANGUAGES['RU']  # По умолчанию русский язык
    return user_states[phone_number]

def update_user_state(phone_number, new_state):
    """Обновление состояния пользователя"""
    user_states[phone_number] = new_state

def save_user_data(phone_number, key, value):
    """Сохранение данных пользователя"""
    if phone_number not in user_data:
        user_data[phone_number] = {}
    user_data[phone_number][key] = value

def set_user_type(phone_number, user_type):
    """Установка типа пользователя"""
    user_types[phone_number] = user_type

def get_user_type(phone_number):
    """Получение типа пользователя"""
    return user_types.get(phone_number, USER_TYPES['UNKNOWN'])

def set_user_language(phone_number, language):
    """Установка языка пользователя"""
    user_languages[phone_number] = language

def get_user_language(phone_number):
    """Получение языка пользователя"""
    return user_languages.get(phone_number, LANGUAGES['RU'])

def get_message(phone_number, message_key):
    """Получение сообщения на выбранном пользователем языке"""
    language = get_user_language(phone_number)
    return MESSAGES[language].get(message_key, MESSAGES[LANGUAGES['RU']][message_key])  # Используем LANGUAGES['RU'] вместо 'ru'

def send_to_trello(phone_number):
    """Отправка данных в Trello в виде карточки"""
    data = user_data[phone_number]
    user_type = get_user_type(phone_number)
    
    if user_type == USER_TYPES['DEALERSHIP']:
        # Формирование данных автосалона для Trello
        card_name = f'Автосалон: {data.get("name", "Неизвестно")}'
        card_description = f"""
Информация об автосалоне:
Название: {data.get('name', '')}
Адрес: {data.get('address', '')}
Телефон: {phone_number}
Уже сотрудничает: {data.get('already_cooperates', 'Нет')}
Удостоверение: {data.get('id_document', '')}
Техпаспорт: {data.get('tech_passport', '')}
        """
    elif user_type == USER_TYPES['CLIENT']:
        # Формирование данных клиента для Trello
        card_name = f'Клиент: Регистрация гарантии'
        card_description = f"""
Информация о клиенте:
Телефон: {phone_number}
Удостоверение: {data.get('id_document', '')}
Техпаспорт: {data.get('tech_passport', '')}

Информация об автомобиле:
Номер машины: {data.get('car_number', '')}
Город: {data.get('city', '')}
Пробег: {data.get('mileage', '')}
        """
    else:
        # Старая логика или неопределенный тип пользователя
        card_name = f'Заявка от {data.get("name", "Неизвестно")}'
        card_description = f"""
Информация о клиенте:
ФИО: {data.get('name', '')}
Телефон: {phone_number}
Город: {data.get('city', '')}

Информация об автомобиле:
Марка: {data.get('car_brand', '')}
Год выпуска: {data.get('car_year', '')}
Пробег: {data.get('car_mileage', '')}
        """
    
    try:
        # Прямая отправка в Trello через API вместо использования библиотеки
        import requests
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        query_params = {
            'key': TRELLO_API_KEY,
            'token': TRELLO_API_TOKEN,
            'name': card_name,
            'desc': card_description,
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
            logger.info(card_description)
            
            # Можно сохранить в локальный файл для дальнейшего импорта
            try:
                with open('saved_applications.txt', 'a', encoding='utf-8') as f:
                    f.write(f"\n\n--- НОВАЯ ЗАЯВКА: {card_name} ---\n")
                    f.write(card_description)
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
        logger.info(card_description)
        
        # Можно сохранить в локальный файл для дальнейшего импорта
        try:
            with open('saved_applications.txt', 'a', encoding='utf-8') as f:
                f.write(f"\n\n--- НОВАЯ ЗАЯВКА: {card_name} ---\n")
                f.write(card_description)
                f.write("\n--- КОНЕЦ ЗАЯВКИ ---\n")
            logger.info("Данные успешно сохранены в локальный файл")
        except Exception as write_error:
            logger.error(f"Ошибка при записи в файл: {write_error}")
        
        # Успешное завершение, даже если Trello недоступен
        return {'result': True, 'local_save': True}

def is_message_processed(message_id, sender_phone):
    """Проверка, было ли сообщение уже обработано"""
    key = f"{message_id}_{sender_phone}"
    if key in processed_messages:
        return True
    processed_messages[key] = True
    
    # Очистка старых записей, чтобы не переполнять память
    if len(processed_messages) > 1000:  # Ограничиваем количество записей
        # Удаляем первые 200 записей (самые старые)
        keys_to_remove = list(processed_messages.keys())[:200]
        for old_key in keys_to_remove:
            processed_messages.pop(old_key, None)
    
    return False

# Обработчик начальной команды и общей информации
@bot.router.message(command="start")
def start_handler(notification: Notification) -> None:
    """Обработчик команды /start"""
    try:
        # Получаем данные отправителя
        sender_data = notification.event.get('senderData', {})
        sender_phone = sender_data.get('sender', '').split('@')[0]
        sender_name = sender_data.get('senderName', 'Пользователь')
        
        # Сбрасываем состояние пользователя на начальное
        update_user_state(sender_phone, STATES['INITIAL'])
        
        # Отправляем приветственное сообщение
        try:
            greeting_message = get_message(sender_phone, 'greeting')
            notification.answer(greeting_message.format(name=sender_name))
        except KeyError:
            # Если ключа 'greeting' нет в словаре сообщений
            notification.answer(f"Здравствуйте, {sender_name}!")
        
        # Отправляем меню выбора языка
        notification.answer(get_message(sender_phone, 'choose_language'))
        
        logger.info(f"Отправлено приветствие пользователю {sender_phone}")
    except Exception as e:
        logger.error(f"Ошибка в обработчике start_handler: {e}", exc_info=True)
        notification.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

# Обработчик для команды помощи
@bot.router.message(command="help")
def help_handler(notification: Notification) -> None:
    """Обработчик команды /help"""
    try:
        # Получаем данные отправителя
        sender_data = notification.event.get('senderData', {})
        sender_phone = sender_data.get('sender', '').split('@')[0]
        
        # Отправляем сообщение помощи
        help_message = get_message(sender_phone, 'help')
        notification.answer(help_message)
        
        logger.info(f"Отправлена справка пользователю {sender_phone}")
    except Exception as e:
        logger.error(f"Ошибка в обработчике help_handler: {e}", exc_info=True)
        notification.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

# Обработчик для сброса состояния
@bot.router.message(command="reset")
def reset_handler(notification: Notification) -> None:
    """Обработчик команды /reset"""
    try:
        # Получаем данные отправителя
        sender_data = notification.event.get('senderData', {})
        sender_phone = sender_data.get('sender', '').split('@')[0]
        
        # Сбрасываем состояние пользователя
        if sender_phone in user_states:
            update_user_state(sender_phone, STATES['INITIAL'])
            user_data[sender_phone] = {}
        
        # Отправляем сообщение о сбросе
        try:
            reset_message = get_message(sender_phone, 'reset')
            notification.answer(reset_message)
        except KeyError:
            # Если ключа 'reset' нет в словаре сообщений
            notification.answer("Диалог сброшен. Выберите язык для продолжения.")
        
        # Отправляем меню выбора языка
        notification.answer(get_message(sender_phone, 'choose_language'))
        
        logger.info(f"Сброшено состояние для пользователя {sender_phone}")
    except Exception as e:
        logger.error(f"Ошибка в обработчике reset_handler: {e}", exc_info=True)
        notification.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

# Основной обработчик для всех входящих сообщений
@bot.router.message()
def message_handler(notification: Notification) -> None:
    """Обработчик всех входящих сообщений"""
    try:
        # Получаем данные о сообщении
        event = notification.event
        message_data = event.get('messageData', {})
        
        # Получаем текст сообщения
        incoming_msg = ''
        if 'textMessageData' in message_data:
            incoming_msg = message_data['textMessageData'].get('textMessage', '').strip()
        elif 'extendedTextMessageData' in message_data:
            incoming_msg = message_data['extendedTextMessageData'].get('text', '').strip()
        elif 'fileMessageData' in message_data:
            incoming_msg = message_data['fileMessageData'].get('caption', '').strip()
        
        # Получаем данные отправителя
        sender_data = event.get('senderData', {})
        sender_phone = sender_data.get('sender', '').split('@')[0]
        
        # Получаем идентификатор сообщения и проверяем, не обрабатывали ли мы его уже
        message_id = event.get('idMessage')
        if is_message_processed(message_id, sender_phone):
            logger.info(f"Сообщение {message_id} от {sender_phone} уже было обработано")
            return
        
        # Получаем текущее состояние пользователя
        current_state = get_user_state(sender_phone)
        logger.info(f"Обрабатываем сообщение от {sender_phone}, состояние: {current_state}, текст: {incoming_msg}")
        
        # Проверка на запрос перезапуска диалога после завершения регистрации
        if current_state in [DEALERSHIP_STATES['COMPLETED'], CLIENT_STATES['COMPLETED']]:
            # Проверяем запрос на перезапуск
            if incoming_msg.lower() in ['9', 'новая заявка', 'жаңа өтінім', 'restart', 'начать заново', 'сначала']:
                # Сбрасываем состояние пользователя на начальное
                update_user_state(sender_phone, STATES['INITIAL'])
                user_data[sender_phone] = {}  # Очищаем данные пользователя
                
                # Отправляем сообщение о перезапуске с меню выбора языка
                notification.answer(get_message(sender_phone, 'choose_language'))
                logger.info(f"Перезапуск диалога для пользователя {sender_phone}")
                return
        
        # Обработка сообщения в зависимости от состояния пользователя
        if current_state == STATES['INITIAL']:
            # Выбор языка
            process_language_selection(notification, sender_phone, incoming_msg)
        elif current_state == STATES['LANGUAGE_SELECTED']:
            # Выбор типа пользователя
            process_user_type_selection(notification, sender_phone, incoming_msg)
        else:
            # Обработка в зависимости от типа пользователя
            user_type = get_user_type(sender_phone)
            if user_type == USER_TYPES['DEALERSHIP']:
                process_dealership_state(notification, sender_phone, incoming_msg, current_state)
            elif user_type == USER_TYPES['CLIENT']:
                process_client_state(notification, sender_phone, incoming_msg, current_state)
            else:
                # Если тип пользователя не определен, предлагаем выбрать заново
                notification.answer(get_message(sender_phone, 'unknown_user_type'))
                update_user_state(sender_phone, STATES['LANGUAGE_SELECTED'])
                notification.answer(get_message(sender_phone, 'user_type_selection'))
                
    except Exception as e:
        logger.error(f"Ошибка в обработчике message_handler: {e}", exc_info=True)
        try:
            notification.answer("Произошла ошибка. Пожалуйста, попробуйте позже или напишите /reset для сброса.")
        except:
            pass

def process_language_selection(notification, sender_phone, text):
    """Обработка выбора языка"""
    if text.lower() in ['1', 'русский', 'рус', 'ru']:
        set_user_language(sender_phone, LANGUAGES['RU'])
        update_user_state(sender_phone, STATES['LANGUAGE_SELECTED'])
        notification.answer(get_message(sender_phone, 'language_selected').format(language='русский'))
        notification.answer(get_message(sender_phone, 'user_type_selection'))
    elif text.lower() in ['2', 'қазақша', 'казахский', 'kz']:
        set_user_language(sender_phone, LANGUAGES['KZ'])
        update_user_state(sender_phone, STATES['LANGUAGE_SELECTED'])
        notification.answer(get_message(sender_phone, 'language_selected').format(language='қазақша'))
        notification.answer(get_message(sender_phone, 'user_type_selection'))
    else:
        notification.answer(get_message(sender_phone, 'invalid_language'))

def process_user_type_selection(notification, sender_phone, text):
    """Обработка выбора типа пользователя"""
    if text.lower() in ['1', 'автосалон', 'дилер', 'dealer']:
        set_user_type(sender_phone, USER_TYPES['DEALERSHIP'])
        update_user_state(sender_phone, DEALERSHIP_STATES['WAITING_FOR_NAME'])
        notification.answer(get_message(sender_phone, 'dealership_selected'))
        notification.answer(get_message(sender_phone, 'ask_dealership_name'))
    elif text.lower() in ['2', 'клиент', 'покупатель', 'client']:
        set_user_type(sender_phone, USER_TYPES['CLIENT'])
        update_user_state(sender_phone, CLIENT_STATES['WAITING_FOR_ID_DOCUMENT'])
        notification.answer(get_message(sender_phone, 'client_selected'))
        notification.answer(get_message(sender_phone, 'ask_id_document'))
    else:
        notification.answer(get_message(sender_phone, 'invalid_user_type'))

def process_dealership_state(notification, sender_phone, text, current_state):
    """Обработка состояний для автосалона"""
    if current_state == DEALERSHIP_STATES['WAITING_FOR_NAME']:
        save_user_data(sender_phone, 'name', text)
        update_user_state(sender_phone, DEALERSHIP_STATES['WAITING_FOR_ADDRESS'])
        notification.answer(get_message(sender_phone, 'ask_dealership_address'))
    elif current_state == DEALERSHIP_STATES['WAITING_FOR_ADDRESS']:
        save_user_data(sender_phone, 'address', text)
        update_user_state(sender_phone, DEALERSHIP_STATES['WAITING_FOR_COOPERATION'])
        notification.answer(get_message(sender_phone, 'ask_already_cooperates'))
    elif current_state == DEALERSHIP_STATES['WAITING_FOR_COOPERATION']:
        save_user_data(sender_phone, 'already_cooperates', text)
        update_user_state(sender_phone, DEALERSHIP_STATES['WAITING_FOR_ID_DOCUMENT'])
        notification.answer(get_message(sender_phone, 'ask_id_document'))
    elif current_state == DEALERSHIP_STATES['WAITING_FOR_ID_DOCUMENT']:
        # Проверяем, отправлен ли файл
        message_data = notification.event.get('messageData', {})
        if 'fileMessageData' in message_data:
            file_data = message_data['fileMessageData']
            file_name = file_data.get('fileName', 'id_document.jpg')
            file_url = file_data.get('downloadUrl', '')
            save_user_data(sender_phone, 'id_document', file_url)
            update_user_state(sender_phone, DEALERSHIP_STATES['WAITING_FOR_TECHPASSPORT'])
            notification.answer(get_message(sender_phone, 'file_received'))
            notification.answer(get_message(sender_phone, 'ask_tech_passport'))
        else:
            notification.answer(get_message(sender_phone, 'ask_file_not_text'))
    elif current_state == DEALERSHIP_STATES['WAITING_FOR_TECHPASSPORT']:
        # Проверяем, отправлен ли файл
        message_data = notification.event.get('messageData', {})
        if 'fileMessageData' in message_data:
            file_data = message_data['fileMessageData']
            file_name = file_data.get('fileName', 'tech_passport.jpg')
            file_url = file_data.get('downloadUrl', '')
            save_user_data(sender_phone, 'tech_passport', file_url)
            update_user_state(sender_phone, DEALERSHIP_STATES['COMPLETED'])
            notification.answer(get_message(sender_phone, 'file_received'))
            
            # Отправляем данные в Trello и завершаем регистрацию
            send_to_trello(sender_phone)
            notification.answer(get_message(sender_phone, 'dealership_registration_completed'))
            
            # Предлагаем начать заново при необходимости
            notification.answer(get_message(sender_phone, 'ask_restart'))
        else:
            notification.answer(get_message(sender_phone, 'ask_file_not_text'))

def process_client_state(notification, sender_phone, text, current_state):
    """Обработка состояний для клиента"""
    if current_state == CLIENT_STATES['WAITING_FOR_ID_DOCUMENT']:
        # Проверяем, отправлен ли файл
        message_data = notification.event.get('messageData', {})
        if 'fileMessageData' in message_data:
            file_data = message_data['fileMessageData']
            file_name = file_data.get('fileName', 'id_document.jpg')
            file_url = file_data.get('downloadUrl', '')
            save_user_data(sender_phone, 'id_document', file_url)
            update_user_state(sender_phone, CLIENT_STATES['WAITING_FOR_TECHPASSPORT'])
            notification.answer(get_message(sender_phone, 'file_received'))
            notification.answer(get_message(sender_phone, 'ask_tech_passport'))
        else:
            notification.answer(get_message(sender_phone, 'ask_file_not_text'))
    elif current_state == CLIENT_STATES['WAITING_FOR_TECHPASSPORT']:
        # Проверяем, отправлен ли файл
        message_data = notification.event.get('messageData', {})
        if 'fileMessageData' in message_data:
            file_data = message_data['fileMessageData']
            file_name = file_data.get('fileName', 'tech_passport.jpg')
            file_url = file_data.get('downloadUrl', '')
            save_user_data(sender_phone, 'tech_passport', file_url)
            update_user_state(sender_phone, CLIENT_STATES['WAITING_FOR_CAR_NUMBER'])
            notification.answer(get_message(sender_phone, 'file_received'))
            notification.answer(get_message(sender_phone, 'ask_car_number'))
        else:
            notification.answer(get_message(sender_phone, 'ask_file_not_text'))
    elif current_state == CLIENT_STATES['WAITING_FOR_CAR_NUMBER']:
        save_user_data(sender_phone, 'car_number', text)
        update_user_state(sender_phone, CLIENT_STATES['WAITING_FOR_CITY'])
        notification.answer(get_message(sender_phone, 'ask_city'))
    elif current_state == CLIENT_STATES['WAITING_FOR_CITY']:
        save_user_data(sender_phone, 'city', text)
        update_user_state(sender_phone, CLIENT_STATES['WAITING_FOR_MILEAGE'])
        notification.answer(get_message(sender_phone, 'ask_mileage'))
    elif current_state == CLIENT_STATES['WAITING_FOR_MILEAGE']:
        save_user_data(sender_phone, 'mileage', text)
        update_user_state(sender_phone, CLIENT_STATES['COMPLETED'])
        
        # Отправляем данные в Trello и завершаем регистрацию
        send_to_trello(sender_phone)
        notification.answer(get_message(sender_phone, 'client_registration_completed'))
        
        # Предлагаем начать заново при необходимости
        notification.answer(get_message(sender_phone, 'ask_restart'))

if __name__ == '__main__':
    bot.run_forever()