import telebot
from telebot import types
import sqlite3
#Токен телеграмм-бота
bot = telebot.TeleBot('8025930490:AAES2tVXdWml4-DErkZTmS8t6ocA6eeyHGE')
name = None

# \start
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup()
    # Создание кнопок
    btn1 = types.KeyboardButton('Посмотреть окна записи')
    btn2 = types.KeyboardButton('Посмотреть сведения о своей записи')
    btn3 = types.KeyboardButton('Обратиться к админстратору')
    markup.add(btn1)
    markup.add(btn2)
    markup.add(btn3)
    # Вывод текста при выполнении комманды \start
    bot.send_message(message.chat.id, 'Привет!', reply_markup=markup)
    bot.register_next_step_handler(message, on_click)

# Обработка кнопок
def on_click(message):
    if message.text == 'Посмотреть окна записи':
        bot.send_message(message.chat.id, 'Окна открылись')
    elif message.text == 'Посмотреть сведения о своей записи':
        bot.send_message(message.chat.id, 'Сведения о записи открылись')
    elif message.text == 'Обратиться к админстратору':
        bot.send_message(message.chat.id, 'Администратор оповещён')

# \admin
@bot.message_handler(commands=['admin'])
def admin(message):
    conn = sqlite3.connect('nailoveBD.sql')
    cur = conn.cursor()
    #подключение БД и создание её
    cur.execute('CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, name varchar(50), pass varchar(50))')
    conn.commit()
    cur.close()
    conn.close()

    bot.send_message(message.chat.id, 'Регистрация! Введите имя')
    bot.register_next_step_handler(message, user_name)

def user_name(message):
    global name
    name = message.text.strip()
    bot.send_message(message.chat.id, 'Введите пароль')
    bot.register_next_step_handler(message, user_pass)

def user_pass(message):
    password = message.text.strip()

    conn = sqlite3.connect('nailoveBD.sql')
    cur = conn.cursor()

    # добавление данных в таблицу
    cur.execute("INSERT INTO users (name, pass) VALUES ('%s', '%s')" %(name, password))
    conn.commit()
    cur.close()
    conn.close()

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton('Список пользователей', callback_data='users'))
    bot.send_message(message.chat.id, 'Пользователь зарегистрирован', reply_markup=markup)

# Обработчик нажатия на кнопку 'Список пользователей'
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    conn = sqlite3.connect('nailoveBD.sql')
    cur = conn.cursor()

    cur.execute('SELECT * FROM users')
    users = cur.fetchall()

    info = ''
    for el in users:
        info += f'Имя: {el[1]}, Пароль: {el[2]}\n'

    cur.close()
    conn.close()
    bot.send_message(call.message.chat.id, info)

# Обработка текста, который ввёл пользователь
@bot.message_handler()
def get_text(messege):
    if messege.text.lower() == 'привет':
        bot.send_message(messege.chat.id, f'Привет, {messege.from_user.first_name} {messege.from_user.last_name}!')
    elif messege.text.lower() == 'id':
        bot.reply_to(messege, f'ID: {messege.from_user.id}')

bot.polling(none_stop=True)