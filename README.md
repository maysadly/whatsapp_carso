# WhatsApp Бот для сбора данных и интеграции с Trello

Этот бот собирает информацию от клиентов через WhatsApp и отправляет ее в Trello в виде карточек.

## Собираемая информация

- ФИО клиента
- Город
- Марка автомобиля
- Год выпуска автомобиля
- Пробег автомобиля
- Номер телефона клиента (получается автоматически из WhatsApp)

## Настройка

1. Установите необходимые зависимости:
```
pip install -r requirements.txt
```

2. Настройте файл `.env`, указав свои учетные данные:
```
# waApi WhatsApp
WAAPI_URL=https://api.waapi.io/v1
WAAPI_TOKEN=your_waapi_token

# Trello API
TRELLO_API_KEY=your_trello_api_key
TRELLO_API_TOKEN=your_trello_api_token
TRELLO_BOARD_ID=your_trello_board_id
TRELLO_LIST_ID=your_trello_list_id
```

3. Настройте waApi:
   - Зарегистрируйте аккаунт на [waApi](https://waapi.io/)
   - Получите API-токен для своего аккаунта
   - Настройте webhook URL на ваш сервер: `https://ваш-домен.com/webhook`

4. Настройте Trello:
   - Получите API ключ и токен в [Trello Developer](https://trello.com/app-key)
   - Создайте доску в Trello и получите ее ID (доступен в URL)
   - Создайте список на доске (например, "Входящие заявки") и получите его ID

## Запуск

Для локального запуска бота с туннелем ngrok выполните:
```
./run_with_ngrok.sh
```

Для запуска в продакшн-среде рекомендуется настроить WSGI-сервер, например Gunicorn:
```
gunicorn -w 4 app:app -b 0.0.0.0:5050
```

## Как это работает

1. Клиент отправляет сообщение боту в WhatsApp
2. Бот запрашивает поочередно информацию о клиенте и его автомобиле
3. После получения всех данных, информация отправляется в Trello через API
4. Создается новая карточка в указанном списке Trello с собранными данными

## Расширение функциональности

Вы можете добавить дополнительные поля для сбора информации, отредактировав:
1. Список состояний (`STATES`) в `config.py`
2. Обработчик сообщений в `app.py`
3. Функцию отправки данных в Trello (`send_to_trello`) в `app.py`