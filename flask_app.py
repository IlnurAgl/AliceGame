from flask import Flask, request
import logging
import random
import json
# Импорт библиотек


# Глобальная переменная для хранения данных пользователя
sessionStorage = {}

# Импорт всех загадок из файла
with open('/home/HHsodmHH/mysite/filename.json', 'r', encoding='utf-8') as f:
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

    # Записать логи в файл
    logging.info('Request: %r', response)

    return json.dumps(response)


# Функция для обработки ответов пользователя
def handle_dialog(res, req):

    # Получение id пользователя
    user_id = req['session']['user_id']

    # Если сессия новая
    if req['session']['new']:
        # Приветствие
        res['response']['text'] = 'Привет! Как тебя зовут?'
        sessionStorage[user_id] = {
            'first_name': None
        }
        return

    # Если пользователь не ввел свое имя
    if not sessionStorage[user_id]['first_name']:
        # Получение имени пользователя
        first_name = get_first_name(req)
        if first_name is None:
            # Если пользователь ввел не имя
            res['response']['text'] = 'Не расслышала имя. Повтори, пожалуйста!'
            return
        else:
            # Если пользователь ввел имя
            sessionStorage[user_id]['first_name'] = first_name
            text = f'Приятно познакомиться, {first_name.title()}.'
            text += 'Я Алиса. Напиши "Загадку"'
            res['response']['text'] = text
            return

    # Если пользователь попросил загадку
    elif 'загадку' in req['request']['nlu']['tokens']:
        # Случайная загадка из словаря с загадками
        res['response']['text'] = random.choice(list(data))
        return


# Функция для получения имени пользователя
def get_first_name(req):
    # перебираем сущности
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            # Если есть сущность с ключом 'first_name'
            # то возвращаем её значение.
            # Во всех остальных случаях возвращаем None.
            return entity['value'].get('first_name', None)


# проверка на источник запуска программы
if __name__ == '__main__':
    # Запуск приложения
    app.run()
