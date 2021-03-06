from flask import Flask, request
import logging
import random
import json
import requests
from cities import cities
from math import sin, cos, sqrt, atan2, radians
# Импорт библиотек

# Глобальная переменная для хранения данных пользователя
sessionStorage = {}

# Математические операторы
operators = ['/', '*', '+', '-']

# Импорт всех загадок из файла
with open('/home/HHsodmHH/mysite/filename.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Кнопки Да, Нет
buttonsYesNo = [
    {
        'title': 'Да',
        'hide': True
    },
    {
        'title': 'Нет',
        'hide': True
    }
]

# Кнопки с названиями игр
buttonsGames = [
    {
        'title': 'Загадку',
        'hide': True
    },
    {
        'title': 'Пример',
        'hide': True
    },
    {
        'title': 'Города',
        'hide': True
    }
]

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
            'exp': '',
            'distance': '',
            'cities': True
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
            text += 'Я Алиса. Напиши "Загадку" или "Пример" или "Города" '
            text += 'для выбора игры'
            res['response']['text'] = text
            return

    # Если пользователь попросил подсказку
    elif 'подсказку' in req['request']['nlu']['tokens']:
        # Вывести случайную букву из ответа
        if sessionStorage[user_id]['mystery']:
            hint = sessionStorage[user_id]['hint']
            ans = sessionStorage[user_id]['answer']
            n = random.randint(0, len(hint) - 1)

            # Добавляем букву в подсказку
            while hint[n] != '*' and '*' in hint:
                n = random.randint(0, len(hint) - 1)
            hint = hint[:n] + ' '.join(ans)[n] + hint[n + 1:]

            # Вывод подсказки
            res['response']['text'] = hint

            # Доавбление кнопки подсказки
            res['response']['buttons'] = [
                {
                    'title': 'Подсказку',
                    'hide': True
                },
                {
                    'title': 'Ответ',
                    'hide': True
                }
            ]

            # Изменение подсказки в сессии
            sessionStorage[user_id]['hint'] = hint
            return

    # Если пользователь попросил ответ
    elif 'ответ' in req['request']['nlu']['tokens']:
        # Если запущена игра про загадки
        if sessionStorage[user_id]['mystery']:
            # Вывод ответ
            ans = sessionStorage[user_id]['answer']
            res['response']['text'] = 'Ответ: ' + ' '.join(ans)

            # Предложение сыграть еще раз
            res['response']['text'] += '. Сыграем еще?'

            # Кнопки для выбора ответа
            res['response']['buttons'] = buttonsYesNo

            # Обнуление сессии
            sessionStorage[user_id]['answer'] = ''
            return
        # Если запущена игра для решения примеров
        elif sessionStorage[user_id]['math']:
            # Вывод ответа
            res['response']['text'] = 'Ответ: '
            res['response']['text'] += sessionStorage[user_id]['exp']

            # Предложение сыграть еще раз
            res['response']['text'] += '. Сыграем еще?'

            # Кнопки для выбора ответа
            res['response']['buttons'] = buttonsYesNo

            # Обнуление сессии
            sessionStorage[user_id]['exp'] = ''
            return

        # Если игра в расстояние между городами
        elif sessionStorage[user_id]['cities']:
            # Вывод ответа
            result = sessionStorage[user_id]['distance']
            res['response']['text'] = 'Ответ: '
            res['response']['text'] += str(int(result)) + 'м'

            # Предложение сыграть еще раз
            res['response']['text'] += '. Сыграем еще?'

            # Кнопки для выбора ответа
            res['response']['buttons'] = buttonsYesNo

            # Обнуление сессии
            sessionStorage[user_id]['distance'] = ''
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
            res['response']['buttons'] = buttonsYesNo

            # Удаление ответа из сессии
            sessionStorage[user_id]['answer'] = ''
        return

    # Если пользователь решил решить пример
    elif sessionStorage[user_id]['exp']:
        result = req['request']['nlu']['tokens'][0]
        # Если ответ не правильный
        if sessionStorage[user_id]['exp'] != result:
            res['response']['text'] = 'Неправильно!('
        else:
            # Если правильный очистка ответа
            res['response']['text'] = 'Правильно! Продолжим играть?'

            # Кнопки для ответа
            res['response']['buttons'] = buttonsYesNo

            # Обнуление ответа
            sessionStorage[user_id]['exp'] = ''
        return

    # Если пользователь выбрал игру в города
    elif sessionStorage[user_id]['distance']:
        # Получение ответа пользователя
        result = req['request']['nlu']['tokens'][0]
        if int(result) > sessionStorage[user_id]['distance']:
            res['response']['text'] = 'Меньше'
            res['response']['buttons'] = [
                {
                    'title': 'Ответ',
                    'hide': True
                }
            ]
        elif int(result) < int(sessionStorage[user_id]['distance']):
            res['response']['text'] = 'Больше'
            res['response']['buttons'] = [
                {
                    'title': 'Ответ',
                    'hide': True
                }
            ]
        else:
            res['response']['text'] = 'Правильно! Сыграем еще?'
            # Кнопки для ответа
            res['response']['buttons'] = buttonsYesNo
        return

    # Если пользователь попросил загадку
    elif 'загадку' in req['request']['nlu']['tokens']:
        # Случайная загадка из словаря с загадками
        question = random.choice(list(data))
        res['response']['text'] = question

        # Доавбление кнопки подсказки
        res['response']['buttons'] = [
            {
                'title': 'Подсказку',
                'hide': True
            },
            {
                'title': 'Ответ',
                'hide': True
            }
        ]

        # Запись в сессию случайной загадки
        sessionStorage[user_id]['answer'] = data[question].split()
        sessionStorage[user_id]['mystery'] = True
        sessionStorage[user_id]['hint'] = len(data[question]) * '*'
        return

    # Если пользователь попросил пример
    elif 'пример' in req['request']['nlu']['tokens']:
        # Запись в сессию
        sessionStorage[user_id]['math'] = True

        # Создание примера
        exp = str(random.randint(0, 100))
        op = str(random.choice(operators)[0])
        exp += op
        exp += str(random.randint(0, 100))

        # Если деление, то проверка на целочисленность ответа
        if op == '/':
            first = random.randint(1, 100)
            second = random.randint(1, 100)
            # Пока первое не делится на второе
            while first % second != 0:
                first = random.randint(1, 100)
                second = random.randint(1, 100)
            exp = str(first) + op + str(second)

        # Вычисление результата
        result = int(eval(exp))
        # Если результат меньше нуля
        while result < 0:
            exp = str(random.randint(1, 100))
            exp += '-'
            exp += str(random.randint(1, 100))
            result = int(eval(exp))

        # Отправка примера пользователю
        res['response']['text'] = str(exp)
        # Добавление кнопок
        res['response']['buttons'] = [
            {
                'title': 'Ответ',
                'hide': True
            }
        ]
        # Запись ответа в сессию
        sessionStorage[user_id]['exp'] = str(result)
        return

    # Игра в отгадывание расстояние между городами
    elif 'города' in req['request']['nlu']['tokens']:
        # Получение двух городов
        first = str(random.choice(cities))
        second = str(random.choice(cities))
        while first == second:
            first = str(random.choice(cities))

        # Запись игры в сессию
        sessionStorage[user_id]['cities'] = True

        # Запись дистанции в сессию
        distance = get_distance(
            get_coordinates(first), get_coordinates(second))
        sessionStorage[user_id]['distance'] = int(distance)

        # Вывод результат
        res['response']['text'] = 'Отгадай расстояние между городами '
        res['response']['text'] += first + ' и '
        res['response']['text'] += second
        res['response']['text'] = [
            {
                'title': 'Ответ',
                'hide': True
            }
        ]
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

        # Создать новый пример
        elif sessionStorage[user_id]['math']:
            # Создание примера
            exp = str(random.randint(0, 100))
            op = str(random.choice(operators)[0])
            exp += op
            exp += str(random.randint(0, 100))

            # Если деление, то проверка на целочисленность ответа
            if op == '/':
                first = random.randint(1, 100)
                second = random.randint(1, 100)
                # Пока первое не делится на второе
                while first % second != 0:
                    first = random.randint(1, 100)
                    second = random.randint(1, 100)
                exp = str(first) + op + str(second)

            # Вычисление результата
            result = int(eval(exp))
            while result < 0:
                exp = str(random.randint(1, 100))
                exp += '-'
                exp += str(random.randint(1, 100))
                result = int(eval(exp))

            # Отправка примера пользователю
            res['response']['text'] = str(exp)
            # Запись ответа в сессию
            sessionStorage[user_id]['exp'] = str(result)
            return

        # Новая пара городов
        elif sessionStorage[user_id]['cities']:
            # Получение двух городов
            first = str(random.choice(cities))
            second = str(random.choice(cities))
            while first == second:
                first = str(random.choice(cities))

            # Запись игры в сессию
            sessionStorage[user_id]['cities'] = True

            # Запись дистанции в сессию
            distance = get_distance(
                get_coordinates(first), get_coordinates(second))
            sessionStorage[user_id]['distance'] = int(distance)

            # Вывод результат
            res['response']['text'] = 'Отгадай расстояние между городами '
            res['response']['text'] += first + ' и '
            res['response']['text'] += second
            return

    # Если пользователь решил закончить игру
    elif 'нет' in req['request']['nlu']['tokens']:
        # Конец игр
        sessionStorage[user_id]['mystery'] = False
        sessionStorage[user_id]['math'] = False
        sessionStorage[user_id]['cities'] = False

        # Предложение выбрать новую игру
        res['response']['text'] = 'Выбери игру'

        # Кнопки для выбора игры
        res['response']['buttons'] = buttonsGames
        return

    # Если пользователь запрос помощь о приложении
    elif 'помощь' in req['request']['nlu']['tokens']:
        res['response']['text'] = 'Приложение для игры в загадки и тренировку '
        res['response']['text'] += 'решения легких математических примеров'
        return

    # Если пользователь спросил "Что ты умеешь?"
    elif 'умеешь' in req['request']['nlu']['tokens']:
        res['response']['text'] = 'Я могу загадать загадку или придумать '
        res['response']['text'] += 'легкий математический пример'

        # Кнопки для начала игры
        res['response']['buttons'] = buttonsGames
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


# Функция для получения координат города
def get_coordinates(city):

    # url yandex api geocode
    url = "https://geocode-maps.yandex.ru/1.x/"

    # Параметры для запроса
    params = {
        'geocode': city,
        'format': 'json'
    }

    # Получение результата
    response = requests.get(url, params)
    # Перобразование в json формат
    json = response.json()
    point_str = json['response']['GeoObjectCollection']['featureMember']
    point_str = point_str[0]['GeoObject']['Point']['pos']
    point_array = [float(x) for x in point_str.split(' ')]

    # Возвращение точки
    return point_array


# Функция для получения расстояния между координатами
def get_distance(p1, p2):

    R = 6373.0

    # Получение широт и долгот
    lon1 = radians(p1[0])
    lat1 = radians(p1[1])
    lon2 = radians(p2[0])
    lat2 = radians(p2[1])

    # Вычисление расстояния
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Вычисление расстояние
    distance = R * c
    # Возвращение расстояния
    return distance


# проверка на источник запуска программы
if __name__ == '__main__':
    # Запуск приложения
    app.run()
