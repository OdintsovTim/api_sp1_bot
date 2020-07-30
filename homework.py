import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(filename='sms.log', level=logging.ERROR)

PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'

bot = telegram.Bot(token=TELEGRAM_TOKEN)

def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    if homework.get('status') == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    elif homework.get('status') == 'approved':
        verdict = ('Ревьюеру всё понравилось, можно '
                   'приступать к следующему уроку.')
    else:
        logging.error('Возникла ошибка: похоже изменился формат выдачи данных')
        raise Exception('Похоже изменился формат выдачи данных')

    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    if current_timestamp is None:
        logging.error('Возникла ошибка: похоже изменился формат выдачи данных')
        raise Exception('Похоже изменился формат выдачи данных')

    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    params = {
        'from_date': current_timestamp,
    }

    try:
        homework_statuses = requests.get(URL, params=params, headers=headers)
    except requests.exceptions.ConnectionError as e:
        logging.error(f'Возникла ошибка: {e}')
        raise

    return homework_statuses.json()


def send_message(message):

    try:
        return bot.send_message(chat_id=CHAT_ID, text=message)
    except telegram.error.NetworkError as e:
        logging.error(f'Возникла ошибка: {e}')
        raise


def main():
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(new_homework.get('homeworks')[0])
                )
            current_timestamp = new_homework.get('current_date')
            time.sleep(1200)

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
