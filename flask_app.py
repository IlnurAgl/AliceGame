from flask import Flask, request
import logging
import random
import json
# Импорт библиотек


# Глобальная переменная для хранения данных пользователя
sessionStorage = {}

# Импорт всех загадок из файла
with open('filename.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Конфигурация для создания логов
logging.basicConfig(
    level=logging.INFO,
    filename='app.log',
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)


# Создание приложения
app = Flask(__name__)


# Создение ответа на пост запросы
@app.route('/post', methods=['POST'])
def main():
    # Записать логов в файл
    logging.info('Request: %r', request.json)
    # Создание сессии
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    # Вызов функции для обработки ответов пользователя
    handle_dialog(response, request.json)
    # Записать логов в файл
    logging.info('Request: %r', response)


# Функция для обработки ответов пользователя
def handle_dialog(res, req):
    # Если сессия новая
    if req['session']['new']:
        # Приветствие
        res['response']['text'] = 'Привет! Если хочешь отгадать загадку, напишу загадку'
        # Создание кнопок для ответа
        res['response']['buttons'] = [
            {
                'title': 'Загадка',
                'hide': True
            }
        ]
        return
    # Если пользователь попросил загадку
    elif 'Загадка' in req['request']['nlu']['tokens']:
        # Случайная загадка из словаря с загадками
        res['response']['text'] = random.choice(data.keys())


# проверка на источник запуска программы
if __name__ == '__main__':
    # Запуск приложения
    app.run()
