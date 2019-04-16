from flask import Flask, request
import logging
import random
import json
# Импорт библиотек


# Глобальная переменная для хранения данных пользователя
sessionStorage = {}

# Математические операторы
operators = ['/', '*', '+', '-']

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
            'first_name': None,
            'answer': '',
            'math': False,
            'mystery': False,
            'exp': ''
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
            sessionStorage[user_id]['answer'] = ''
            sessionStorage[user_id]['first_name'] = first_name
            text = f'Приятно познакомиться, {first_name.title()}.'
            text += 'Я Алиса. Напиши "Загадку"'
            res['response']['text'] = text
            return

    # Если пользователь начал игру
    elif sessionStorage[user_id]['answer']:
        t = False
        # Проверка ответа пользователя
        for i in sessionStorage[user_id]['answer']:
            if i.lower() not in req['request']['nlu']['tokens']:
                t = True
                break
        if t:
            # Если пользователь ошибся
            res['response']['text'] = 'Неправильно!'
        else:
            # Если пользователь ответил правиль
            res['response']['text'] = 'Правильно! Продолжим играть?'
            res['response']['buttons'] = [
                {
                    'title': 'Да',
                    'hide': True
                },
                {
                    'title': 'Нет',
                    'hide': True
                }
            ]
            # Удаление ответа из сессии
            sessionStorage[user_id]['answer'] = ''
        return

    # Если пользователь решил решить пример
    elif sessionStorage[user_id]['exp']:
        # Если ответ не правильный
        result = req['request']['nlu']['tokens'][0]
        if sessionStorage[user_id]['exp'] != result:
            res['response']['text'] = 'Неправильно!'
        else:
            # Если правильный очистка ответа
            res['response']['text'] = 'Правильно!'
            sessionStorage[user_id]['exp'] = ''
        return

    # Если пользователь попросил загадку
    elif 'загадку' in req['request']['nlu']['tokens']:
        # Случайная загадка из словаря с загадками
        question = random.choice(list(data))
        res['response']['text'] = question
        # Запись в сессию случайной загадки
        sessionStorage[user_id]['answer'] = data[question].split()
        sessionStorage[user_id]['mystery'] = True
        return

    # Если пользователь попросил пример
    elif 'пример' in req['request']['nlu']['tokens']:
        # Запись в сессию
        sessionStorage[user_id]['math'] = True

        # Создание примера
        exp = str(random.randint(0, 100))
        exp += str(random.choice(operators)[0])
        exp += str(random.randint(0, 100))
        res['response']['text'] = exp
        # Запись ответа в сессию
        sessionStorage[user_id]['exp'] = str(eval(exp))
        return

    # Если пользователь хочет продолжить игру
    elif 'да' in req['request']['nlu']['tokens']:
        # Случайная загадка из словаря с загадками
        if sessionStorage[user_id]['mystery']:
            question = random.choice(list(data))
            res['response']['text'] = question
            # Запись в сессию случайной загадки
            sessionStorage[user_id]['answer'] = data[question].split()
            return

    # Если пользователь решил закончить игру
    elif 'нет' in req['request']['nlu']['tokens']:
        # Конец игр
        sessionStorage[user_id]['mystery'] = False
        sessionStorage[user_id]['math'] = False
        # Предложение выбрать новую игру
        res['response']['text'] = 'Выбери игру'
        return

    # Если пользователь ввел неизвестную команду
    res['response']['text'] = 'Я не смогла понять ваш ответ'


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
