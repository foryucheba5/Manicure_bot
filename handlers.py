import telebot
import re
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import date, datetime


from db import  is_admin, add_admin, add_master, add_service, add_service_master_price, add_appointments, \
    get_services, get_serv, get_master, edt_service_name, get_masters, del_service, edt_service_descr, master_in_serv,\
    edt_service_price

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

SERV_ID = {}
SERV_NAME = {}
SERV_DESCRIPTION = {}
SERV_ID_ADD = {}
MASTER_ID = {}

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
        bot.register_next_step_handler(message, on_click) # тут надо будет поменять на следующий шаг и изменить функцию elif message.text == 'Посмотреть сведения о своей записи':
    elif message.text == 'Посмотреть сведения о своей записи':
        bot.send_message(message.chat.id, 'Сведения о записи открылись')
        bot.register_next_step_handler(message, on_click)
    elif message.text == 'Обратиться к админстратору':
        bot.send_message(message.chat.id, 'Администратор оповещён')
        bot.register_next_step_handler(message, on_click)
    elif message.text == 'Админ-панель':
        markup_admin = types.ReplyKeyboardMarkup()
        btn_master = types.KeyboardButton('Добавить нового мастера')
        btn_services = types.KeyboardButton('Каталог услуг')
        btn_exit = types.KeyboardButton('В главное меню')
        markup_admin.add(btn_master)
        markup_admin.add(btn_services)
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
    elif message.text == 'Каталог услуг':
        print_services(message)

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
    add_admin('Аня', '89093314566', message.from_user.id)

def print_services(message):
    markup = InlineKeyboardMarkup()
    btn_add_serv = InlineKeyboardButton(text="Добавить новую услугу", callback_data="add_serv_name")
    markup.add(btn_add_serv)
    services = get_services()

    for service in services:
        btn_edt = InlineKeyboardButton(text=service[1], callback_data="edt_serv#" + str(service[0]) + "#" + service[1])
        markup.add(btn_edt)

    btn_main = InlineKeyboardButton(text="В главное меню", callback_data="main")
    markup.add(btn_main)
    bot.send_message(message.chat.id, "Каталог услуг", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.split("#")[0] == "edt_serv")
def edt_serv(call):
    service_id = call.data.split("#")[1]
    service_name = call.data.split("#")[2]
    SERV_ID[call.message.chat.id] = service_id

    iter = 0
    text_call = ""
    for serv in get_serv(service_id):
        service_description = serv[0]
        if iter == 0:
            text_call = f"""<b>{service_name} ({service_description})</b>\n\n<b>Мастера:</b>\n"""

        if len(serv) > 1:
            service_prices = serv[1]
            service_master_id = serv[2]
            master_name = get_master(str(service_master_id))
            text_call += f"""{iter + 1}) {master_name} - {service_prices} руб.\n"""
        iter = iter + 1

    markup = InlineKeyboardMarkup(row_width=1)
    title_edt_btn = InlineKeyboardButton(text="Название", callback_data="edt_serv_name")
    descr_edt_btn = InlineKeyboardButton(text="Описание", callback_data="edt_serv_descr")
    master_edt_btn = InlineKeyboardButton(text="Мастера", callback_data="serv_master")
    del_serv_btn = InlineKeyboardButton(text="Удалить", callback_data="del_serv")
    main_btn = InlineKeyboardButton(text="Вернуться в каталог", callback_data="back_cat")
    markup.add(title_edt_btn, descr_edt_btn, master_edt_btn, del_serv_btn, main_btn)
    bot.send_message(call.message.chat.id, text_call, parse_mode="HTML", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.split("#")[0] == "back_cat")
def back_cat(call):
    print_services(call.message)

# Редактирование названия услуги
@bot.callback_query_handler(func=lambda call: call.data.split("#")[0] == "edt_serv_name")
def edt_serv_name(call):
    bot.send_message(call.message.chat.id, "Введите новое название услуги")
    bot.register_next_step_handler(call.message, edt_serv_name_step)

def edt_serv_name_step(message):
    if SERV_ID[message.chat.id] != '' and SERV_ID[message.chat.id] is not None:
        serv_name = message.text
        edt_service_name(SERV_ID[message.chat.id], serv_name)
        bot.send_message(message.chat.id, "Ок. Новое название услуги: " + serv_name)
        print_services(message)

# Редактирование описания услуги
@bot.callback_query_handler(func=lambda call: call.data == "edt_serv_descr")
def edt_serv_descr(call):
    bot.send_message(call.message.chat.id, "Введите новое описание услуги")
    bot.register_next_step_handler(call.message, edt_serv_descr_step)

def edt_serv_descr_step(message):
    if SERV_ID[message.chat.id] != '' and SERV_ID[message.chat.id] is not None:
        serv_descr = message.text
        edt_service_descr(SERV_ID[message.chat.id], serv_descr)
        bot.send_message(message.chat.id, "Ок. Новое описание услуги: " + serv_descr)
        print_services(message)

# Редактирование мастеров в услуге
@bot.callback_query_handler(func=lambda call: call.data == "serv_master")
def serv_master(call):
    markup = InlineKeyboardMarkup()
    masters = get_masters()
    for master in masters:
        master_btn = InlineKeyboardButton(text=master[1], callback_data="add_serv_master#" + str(master[0]))
        markup.add(master_btn)
    bot.send_message(call.message.chat.id, "Укажите мастера: ", reply_markup=markup)


# Добавление новой услуги
@bot.callback_query_handler(func=lambda call: call.data == "add_serv_name")
def add_serv_name(call):
    bot.send_message(call.message.chat.id, "Введите название услуги")
    bot.register_next_step_handler(call.message, add_serv_descr)


def add_serv_descr(message):
    SERV_NAME[message.chat.id] = message.text
    bot.send_message(message.chat.id, "Введите описание услуги")
    bot.register_next_step_handler(message, service)


def service(message):
    if SERV_NAME[message.chat.id] is not None:
        SERV_ID[message.chat.id] = str(add_service(SERV_NAME[message.chat.id], message.text))
        markup = InlineKeyboardMarkup()
        masters = get_masters()
        for master in masters:
            master_btn = InlineKeyboardButton(text=master[1], callback_data="add_serv_master#" + str(master[0]))
            markup.add(master_btn)
        bot.send_message(message.chat.id, "Ок. Услуга создана. Укажите мастера: ", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.split("#")[0] == "add_serv_master")
def add_serv_master(call):
    if call.data.split("#") and call.data.split("#")[0] == "add_serv_master" and call.data.split("#")[1] != '' and call.data.split("#")[1] is not None:
            MASTER_ID[call.message.chat.id] = call.data.split("#")[1]
    bot.send_message(call.message.chat.id, "Введите стоимость услуги")
    bot.register_next_step_handler(call.message, service_master_price)

def service_master_price(message):
    if MASTER_ID[message.chat.id] != '' and MASTER_ID[message.chat.id] is not None:
        serv_price = message.text
        if not master_in_serv(SERV_ID[message.chat.id], MASTER_ID[message.chat.id]):
            add_service_master_price(SERV_ID[message.chat.id], MASTER_ID[message.chat.id], serv_price)
            bot.send_message(message.chat.id, "Мастер успешно назначен!")
        else:
            edt_service_price(SERV_ID[message.chat.id], MASTER_ID[message.chat.id], serv_price)
            bot.send_message(message.chat.id, "Стоимость услуги данного мастера успешно обновлена!")
    print_services(message)

@bot.callback_query_handler(func=lambda call: call.data == "del_serv")
def del_serv_step(call):
    bot.send_message(call.message.chat.id, "Вы уверены, что хотите удалить услугу?")
    bot.register_next_step_handler(call.message, del_serv)

def del_serv(message):
    if message.text == "Да" or message.text == "да":
        del_service(SERV_ID[message.chat.id])
        bot.send_message(message.chat.id, "Услуга удалена!")
    print_services(message)

# Костыль на время, чтобы добавить мастера - введите нужные данные шоб добавить ненастоящего мастера и в боте введите команду /new_master
@bot.message_handler(commands=['new_master'])
def new_master(message):
    add_master('Юнона', '89198345322', '5590353291')

# Костыль на время, чтобы добавить записи - введите нужные данные шоб добавить записи и в боте введите команду /new_appointments
@bot.message_handler(commands=['new_appointments'])
def appointments(message):
    today = date.today().isoformat()  # Преобразуем дату в ISO формат YYYY-MM-DD
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    add_appointments('123', '12', '1', '1', 1)  # Передаем правильные типы данных