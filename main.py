from handlers import bot, send_warning_notification
from db import init_db, find_upcoming_appointments_for_warning
from threading import Thread
from datetime import datetime, timedelta
import time

def daily_warning_job():
    while True:
        now = datetime.now()
        print("Вощёл")
        # if now.hour == 12 and now.minute == 8:  # Выполняется в 11:31 каждый день
        #     appointments = find_upcoming_appointments_for_warning()
        #     if appointments:
        #         send_warning_notification(appointments)
        appointments = find_upcoming_appointments_for_warning()
        print(appointments)
        if appointments:
            print("Отправляю")
            send_warning_notification(appointments)
        else:
            print("Не хочу")
        time.sleep(60)  # Проверять каждые 60 секунд


Thread(target=daily_warning_job).start()

if __name__ == '__main__':
    init_db()  # Инициализация базы данных
    bot.polling(none_stop=True)