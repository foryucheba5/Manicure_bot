import telebot
import re
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from db import  is_admin, add_admin, add_master

#Токен телеграмм-ботаbot = telebot.TeleBot('токен_бота')
bot = telebot.TeleBot('8025930490:AAES2tVXdWml4-DErkZTmS8t6ocA6eeyHGE')
url_master = 'https://t.me/nailove_manicure_bot?start=addMaster'
name = None
btn1 = types.KeyboardButton('Посмотреть окна записи')
btn2 = types.KeyboardButton('Посмотреть сведения о своей записи')
btn4 = types.KeyboardButton('Админ-панель')

user_states = {}
STATES = {
    "WAITING_NAME": 1,
    "WAITING_NUMBER": 2,
}

#главная менюшка на клавиатуре
def main_panel(message):
    markup = types.ReplyKeyboardMarkup()
    admin_is = is_admin(message.from_user.id)
    # Создание кнопок
    if admin_is:
        markup.add(btn1)
        markup.add(btn2)
        markup.add(btn4)
    else:
        markup.add(btn1)
        markup.add(btn2)
    return markup

# \start
@bot.message_handler(commands=['start'])
def start(message):
    if len(message.text.split()) > 1:
        param = message.text.split()[1]
        if param == 'addMaster':
            user_states[message.chat.id] = {"state": STATES["WAITING_NAME"], "data":{}}
            bot.send_message(message.chat.id,"""Привет, красотка \U0001F929 Давай добавим тебя в наш бот \U0001F485 \nТвой номер телефона и профиль не будет доступен для клиентов \U0001F497""")
            bot.send_message(message.chat.id, "Отправь мне своё имя")
    else:
        markup = main_panel(message)
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
    elif message.text == 'Админ-панель':
        markup_admin = types.ReplyKeyboardMarkup()
        btn_master = types.KeyboardButton('Добавить нового мастера')
        btn_exit =  types.KeyboardButton('В главное меню')
        markup_admin.add(btn_master)
        markup_admin.add(btn_exit)
        bot.send_message(message.chat.id, 'Панель адмнистратора: выберите действие', reply_markup=markup_admin)
        bot.register_next_step_handler(message, on_click)
    elif message.text == 'В главное меню':
        markup = main_panel(message)
        bot.send_message(message.chat.id, 'Главное меню: выберите действие', reply_markup=markup)
        bot.register_next_step_handler(message, on_click)
    elif message.text == 'Добавить нового мастера':
        bot.send_message(message.chat.id, 'Перешлите следующее сообщение мастеру:')
        bot.send_message(message.chat.id, "Привет \U0001F497 Нажми <a href='https://t.me/nailove_manicure_bot?start=addMaster'>сюда</a>, чтобы пройти регистрацию в боте нашей студии.",  parse_mode='HTML')
        bot.register_next_step_handler(message, on_click)

# Обработчик для диалога при добавлении мастера
@bot.message_handler(func=lambda message: message.chat.id in user_states)
def handle_message(message):
    chat_id = message.chat.id
    state = user_states[chat_id]["state"]
    if state == STATES["WAITING_NAME"]:
        user_states[chat_id]["data"]["name"] = message.text  # Сохраняем имя
        bot.send_message(message.chat.id, "Отправь мне свой номер")
        user_states[chat_id]["state"] = STATES["WAITING_NUMBER"]
    if state == STATES["WAITING_NUMBER"]:
        if is_valid_phone_number(message.text):
            user_states[chat_id]["data"]["number"] = message.text  # Сохраняем
            n = user_states[chat_id]["data"]["name"]
            number = user_states[chat_id]["data"]["number"]
            # Выводим собранные данные
            summary = f"""<b>Твои данные:</b>\n<b>Имя:</b> {n}\n<b>Телефон:</b> {number}\n"""
            markup = InlineKeyboardMarkup(row_width=1)
            share_button = InlineKeyboardButton(text="Подтвердить данные", callback_data="share_info")
            cancel_button = InlineKeyboardButton(text="Ввести данные снова", callback_data="reload")
            gen_button = InlineKeyboardButton(text="В главное меню", callback_data="main")
            markup.add(share_button, cancel_button, gen_button)
            bot.send_message(chat_id, summary, parse_mode="HTML", reply_markup=markup)
        else:
            bot.send_message(message.chat.id,"Неверный формат номера телефона.\nПожалуйста, введи номер в формате +71234567890 или 81234567890")

# Обработчик нажатия на кнопку 'Подтвердить данные' - добавление мастера
@bot.callback_query_handler(func=lambda call: call.data == 'share_info')
def callback(call):
    chat_id = call.message.chat.id
    if chat_id in user_states:
        n = user_states[chat_id]["data"]["name"]
        number = user_states[chat_id]["data"]["number"]
        ok = add_master(n,number, call.from_user.id)
        markup = main_panel(call.message)
        if ok:
            bot.send_message(call.message.chat.id, "Ты добавлена в бот \U0001F48B", reply_markup=markup)
            bot.register_next_step_handler(call.message, on_click)
        else:
            bot.send_message(call.message.chat.id, "Что-то пошло не так...", reply_markup=markup)
            bot.register_next_step_handler(call.message, on_click)
        del user_states[chat_id]
    else:
        print("Ошибка при добавлении мастера")

# Обработчик нажатия на кнопку 'Ввести данные снова'
@bot.callback_query_handler(func=lambda call: call.data == 'reload')
def callback(call):
    bot.send_message(call.message.chat.id, "Отправь мне своё имя")
    user_states[call.message.chat.id] = {"state": STATES["WAITING_NAME"], "data": {}}

# Обработчик нажатия на кнопку 'Главное меню'
@bot.callback_query_handler(func=lambda call: call.data == 'main')
def callback(call):
    markup = main_panel(call.message)
    bot.send_message(call.message.chat.id, 'Главное меню: выберите действие', reply_markup=markup)
    bot.register_next_step_handler(call.message, on_click)

# Функция для проверки номера телефона
def is_valid_phone_number(phone_number):
    # Регулярное выражение для проверки номера в формате +71234567890 или 81234567890
    pattern = r"^(\+7|8)\d{10}$"
    return re.match(pattern, phone_number) is not None

# Добавить админа - введите нужные данные шоб добавить себя и в боте введите команду /admin
@bot.message_handler(commands=['admin'])
def admin(message):
    add_admin('Марина', '89198345266', message.from_user.id)