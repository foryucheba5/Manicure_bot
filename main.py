from handlers import bot
from db import init_db

if __name__ == '__main__':
    init_db()  # Инициализация базы данных
    bot.polling(none_stop=True)