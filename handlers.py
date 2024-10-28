import telebot
from telebot import types
from db import add_user, get_users

#Токен телеграмм-ботаbot = telebot.TeleBot('токен_бота')
bot = telebot.TeleBot('8025930490:AAES2tVXdWml4-DErkZTmS8t6ocA6eeyHGE')
name = None
#это марина

# \start
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup() # Создание макета
    # Создание кнопок
    btn1 = types.KeyboardButton('Посмотреть окна записи')
    btn2 = types.KeyboardButton('Посмотреть сведения о своей записи')
    btn3 = types.KeyboardButton('Обратиться к админстратору')
    # Добавление кнопок на макет
    markup.add(btn1)
    markup.add(btn2)
    markup.add(btn3)
    # Вывод текста при выполнении комманды \start
    bot.send_message(message.chat.id, 'Привет!', reply_markup=markup) # Вывод сообщения и макета с кнопками
    bot.register_next_step_handler(message, on_click) # Для обработки кнопок

# Обработка кнопок
def on_click(message):
    if message.text == 'Посмотреть окна записи':
        bot.send_message(message.chat.id, 'Окна открылись')
        bot.register_next_step_handler(message, on_click) # тут надо будет поменять на следующий шаг и изменить функцию    elif message.text == 'Посмотреть сведения о своей записи':
    elif message.text == 'Посмотреть сведения о своей записи':
        bot.send_message(message.chat.id, 'Сведения о записи открылись')
        bot.register_next_step_handler(message, on_click)
    elif message.text == 'Обратиться к админстратору':
        bot.send_message(message.chat.id, 'Администратор оповещён')
        bot.register_next_step_handler(message, on_click)

# \admin
@bot.message_handler(commands=['admin'])
def admin(message):
    bot.send_message(message.chat.id, 'Регистрация! Введите имя')
    bot.register_next_step_handler(message, user_name)


def user_name(message):
    global name
    name = message.text.strip()
    bot.send_message(message.chat.id, 'Введите пароль')
    bot.register_next_step_handler(message, user_pass)


def user_pass(message):
    password = message.text.strip()
    add_user(name, password) # Функция добаления пользователя в систему

    markup = telebot.types.InlineKeyboardMarkup() # Создание макета
    markup.add(telebot.types.InlineKeyboardButton('Список пользователей', callback_data='users')) # Добавление кнопки просмотра всех пользователей на макет
    bot.send_message(message.chat.id, 'Пользователь зарегистрирован', reply_markup=markup) # Вывод сообщения и макета с кнопкой

# Обработчик нажатия на кнопку 'Список пользователей'
@bot.callback_query_handler(func=lambda call: call.data == 'users')
def callback(call):
    users = get_users() # Функция вывода всех пользователей

    info = ''
    for el in users:
        info += f'Имя: {el[1]}, Пароль: {el[2]}\n'

    if info:
        bot.send_message(call.message.chat.id, info)
    else:
        bot.send_message(call.message.chat.id, "Нет пользователей.")

# Обработка текста, который ввёл пользователь
@bot.message_handler()
def get_text(message):
    if message.text.lower() == 'привет': # ввод: привет
        bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name} {message.from_user.last_name}!') # вывод: Привет, Имя Фамилия!
    elif message.text.lower() == 'id': # ввод: id
        bot.reply_to(message, f'ID: {message.from_user.id}') # вывод: ID:id_пользователя