import pprint

import telebot
import re
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from datetime import date, timedelta, datetime
import calendar
from typing import Dict, List

from db import is_admin, add_admin, add_master, add_service, add_service_master_price, add_appointments, \
    get_services, get_serv, get_master, edt_service_name, get_masters, del_service, edt_service_descr, master_in_serv, \
    edt_service_price, save_user_to_database, is_user_in_database, get_service_master_price_id, \
    get_available_times_for_date, get_unique_days_in_month_and_year_new, get_unique_months_in_year_new, \
    get_service_detail, get_available_services, get_user_id_by_telegram_id, update_telegram_id, \
    get_service_info_by_service_master_price_id, get_user_info_by_id, get_appointment_id_by_params, \
    update_client_id_in_appointment, rename_user_info, get_user_id_by_telegram_id_show, \
    get_appointments_by_client_id_show, del_user, get_appointments, get_available_services_new, get_service_detail_new, \
    get_unique_active_years_new, check_free_app_for_month_year, get_user_telegram_ids

#Токен телеграмм-ботаbot = telebot.TeleBot('токен_бота')
bot = telebot.TeleBot('7507424407:AAGb_7uu8r27CiYAw23qR2HfTCHpqO8e7Ww')
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

apps = ["09:00-11:00", "11:00-13:00", "14:00-16:00", "16:00-18:00"]

#главная менюшка на клавиатуре
def main_panel(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    admin_is = is_admin(user_id)
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
        markup = main_panel(message.from_user.id)
        # Вывод текста при выполнении комманды \start
        bot.send_message(message.chat.id, 'Привет!', reply_markup=markup) # Вывод сообщения и макета с кнопками
        bot.register_next_step_handler(message, on_click) # Для обработки кнопок

# Обработка кнопок
def on_click(message):
    if message.text == 'Посмотреть окна записи':
        show_services(message.chat.id)
    elif message.text == 'Посмотреть сведения о своей записи':
        show_services_client(message)  # Также передаем весь объект message
    elif message.text == 'Обратиться к админстратору':
        bot.send_message(message.chat.id, 'Администратор оповещён')
        bot.register_next_step_handler(message, on_click)
    elif message.text == 'Админ-панель':
        markup_admin = types.ReplyKeyboardMarkup()
        btn_master = types.KeyboardButton('Добавить нового мастера')
        btn_services = types.KeyboardButton('Каталог услуг')
        btn_exit = types.KeyboardButton('В главное меню')
        btn5 = types.KeyboardButton('Cоздание графика работы мастера')
        btn6 = types.KeyboardButton('Отправить клиентам оповещение об открытии записи')
        markup_admin.add(btn_master)
        markup_admin.add(btn_services)
        markup_admin.add(btn5)
        markup_admin.add(btn6)
        markup_admin.add(btn_exit)
        bot.send_message(message.chat.id, 'Панель адмнистратора: выберите действие', reply_markup=markup_admin)
        bot.register_next_step_handler(message, on_click)
    elif message.text == 'Cоздание графика работы мастера':
        markup = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, "Создание графика работы", reply_markup=markup)
        show_month(message)
    elif message.text == 'В главное меню':
        markup = main_panel(message.from_user.id)
        bot.send_message(message.chat.id, 'Главное меню: выберите действие', reply_markup=markup)
        bot.register_next_step_handler(message, on_click)
    elif message.text == 'Добавить нового мастера':
        bot.send_message(message.chat.id, 'Перешлите следующее сообщение мастеру:')
        bot.send_message(message.chat.id, "Привет \U0001F497 Нажми <a href='https://t.me/nailove_manicure_bot?start=addMaster'>сюда</a>, чтобы пройти регистрацию в боте нашей студии.",  parse_mode='HTML')
        bot.register_next_step_handler(message, on_click)
    elif message.text == 'Каталог услуг':
        print_services(message)
    elif message.text == 'Отправить клиентам оповещение об открытии записи':
        markup = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, "Отправка оповещения клиентам", reply_markup=markup)
        send_notification_client(message)

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
        ok = add_master(n, number, call.from_user.id)
        add_service_master_price('1', '5', '2000')
        client = None
        #add_appointments('2024-12-11', '12:00-14:00', '4', client, '1')  # Передаем правильные типы данных
        #add_appointments('2024-12-11', '14:00-15:00', '4', client, '1')  # Передаем правильные типы данных
        #add_appointments('2024-12-10', '20:00-22:00', '4', client, '1')  # Передаем правильные типы данных
        #add_appointments('2024-12-09', '20:00-22:00', '4', client, '1')  # Передаем правильные типы данных
        #add_appointments('2024-12-08', '20:00-22:00', '4', client, '1')  # Передаем правильные типы данных
        markup = main_panel(call.from_user.id)
        if ok:
            bot.send_message(call.message.chat.id, "Ты добавлена в бот \U0001F48B", reply_markup=markup)
            bot.register_next_step_handler(call.message, on_click)
            print(call.from_user.id)
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
    markup = main_panel(call.from_user.id)
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
    add_admin('Таня', '89883314500', message.from_user.id)


@bot.message_handler(commands=['bez_master'])
def bez_master(message):
    add_service_master_price('1', '3', '2000')


# id
@bot.message_handler(commands=['id'])
def admin(message):
    print(message.from_user.id)

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
    add_master('Гремли', '89108345322', '9890353291')


# Костыль на время
@bot.message_handler(commands=['new_id'])
def new_master(message):
    update_telegram_id(4, 1110154291)


# Костыль на время, чтобы добавить записи - введите нужные данные шоб добавить записи и в боте введите команду /new_appointments
@bot.message_handler(commands=['new_appointments'])
def appointments(message):
    today = date.today().isoformat()  # Преобразуем дату в ISO формат YYYY-MM-DD
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    client = None
    # add_appointments('2025-01-13', '12:00-14:00', '3', client, '1')  # Передаем правильные типы данных мастер варвара
    #add_appointments('2025-12-28', '18:00-20:00', '1', client, '1')  # Передаем правильные типы данных мастер ева
    #add_appointments('2024-12-11', '12:00-14:00', '3', client, '1')  # Передаем правильные типы данных
    #add_appointments('2024-12-11', '14:00-15:00', '3', client, '1')  # Передаем правильные типы данных
    #add_appointments('2024-12-10', '20:00-22:00', '3', client, '1')  # Передаем правильные типы данных
    #add_appointments('2024-12-09', '20:00-22:00', '3', client, '1')  # Передаем правильные типы данных
    #add_appointments('2024-12-08', '20:00-22:00', '3', client, '1')  # Передаем правильные типы данных
    # add_appointments('2024-12-13', current_time, '2', client, '1')  # Передаем правильные типы данных
    # add_appointments('2024-12-14', current_time, '1', client, '1')  # Передаем правильные типы данных
    # add_appointments('2024-11-20', current_time, '3', client, '1')  # Передаем правильные типы данных
    # add_appointments(today, current_time, '2', client, '1')  # Передаем правильные типы данных
    print("Да")

    #add_appointments(today, current_time, '2', client, '1')  # Передаем правильные типы данных


#Измения для функции записи
#Тут эксперемент


# # Функция для генерации клавиатуры с услугами
# def generate_service_keyboard():
#     available_services = get_available_services()
#     markup = types.InlineKeyboardMarkup()
#
#     # Предположим, что функция get_available_services возвращает список словарей,
#     # где каждый словарь содержит 'id' и 'name'
#     for service in available_services:
#         markup.add(types.InlineKeyboardButton(
#             text=service['name'],
#             callback_data=f"service_{service['id']}"
#         ))
#
#     markup.add(types.InlineKeyboardButton("Отмена", callback_data="cancel"))
#     return markup

# Функция для генерации клавиатуры с услугами
# def generate_service_keyboard():
#     available_services = get_available_services()
#     markup = types.InlineKeyboardMarkup()
#
#     for service in available_services:
#         # Добавляем кнопки для каждой услуги
#         markup.add(types.InlineKeyboardButton(
#             text=service['name'],  # Только название услуги
#             callback_data=f"service_{service['id']}"
#         ))
#
#     markup.add(types.InlineKeyboardButton("Отмена", callback_data="cancel"))  # Кнопка отмены
#     return markup

# Функция для генерации клавиатуры с услугами после спринта
def generate_service_keyboard():
    available_services = get_available_services_new()
    markup = types.InlineKeyboardMarkup()

    for service in available_services:
        # Добавляем кнопки для каждой услуги
        markup.add(types.InlineKeyboardButton(
            text=f"{service['name']} ({service['price']} руб.)",  # название и цена
            callback_data=f"service_{service['id']}"
        ))

    markup.add(types.InlineKeyboardButton("Отмена", callback_data="cancel"))  # Кнопка отмены
    return markup



# Создаем кнопку "Вернуться в главное меню"
back_to_main_menu_button = types.KeyboardButton('Вернуться в главное меню')

# Клавиатура с одной кнопкой
no_services_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add(back_to_main_menu_button)


# Функция для обработки возврата в главное меню
def go_to_main_menu(message):
    markup = main_panel(message.from_user.id)
    bot.send_message(message.chat.id, 'Главное меню: выберите действие', reply_markup=markup)
    bot.register_next_step_handler(message, on_click)


# Обработчик нажатия кнопки "Вернуться в главное меню"
@bot.message_handler(func=lambda message: message.text == 'Вернуться в главное меню')
def return_to_main_menu(message):
    go_to_main_menu(message)

def show_services(chat_id):
    available_services = get_available_services_new()
    if len(available_services) > 0:
        # Отправляем сообщение с перечислением услуг
        service_list = "\n".join([f"{service['name']} - {service['description']} - Цена: {service['price']}" for service in available_services])
        bot.send_message(chat_id, f"Доступные услуги:\n{service_list}")
        bot.send_message(chat_id, "Выберите услугу:", reply_markup=generate_service_keyboard())
    else:
        no_services_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton('Вернуться в главное меню'))
        bot.send_message(chat_id, "Нет доступных услуг....", reply_markup=no_services_keyboard)


def show_services_client(message):
    id_telegram = message.chat.id  # Получаем Telegram ID
    client_id = get_user_id_by_telegram_id_show(id_telegram)  # Получаем client_id по Telegram ID

    if client_id is None:
        bot.send_message(message.chat.id, "Пользователь не найден.")
        return

    appointments = get_appointments_by_client_id_show(client_id)  # Получаем записи для клиента

    if not appointments:
        no_services_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add(
            types.KeyboardButton('Вернуться в главное меню'))
        bot.send_message(message.chat.id, "Вы еще не были записаны на услуги", reply_markup=no_services_keyboard)
        return

    # Формируем сообщение с услугами
    services_message = ""
    for index, appointment in enumerate(appointments, start=1):  # Добавляем индексацию записей
        appointment_date, appointment_time, service_name, price, client_name, master_name = appointment
        services_message += (f"Запись {index}\n"
                            f"Услуга: {service_name}\n"
                            f"Мастер: {master_name}\n"
                            f"Стоимость: {price} руб.\n"
                            f"Дата: {appointment_date}\n"
                            f"Время: {appointment_time}\n\n")  # Двойной перенос строки между записями

    services_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add(
        types.KeyboardButton('Вернуться в главное меню'))
    bot.send_message(message.chat.id, services_message.strip(), reply_markup=services_keyboard)  # Убираем лишний пробел в конце












# Функция для генерации клавиатуры с мастерами и ценой
# def generate_master_keyboard(service_id):
#     service_details = get_service_detail(service_id)
#     markup = types.InlineKeyboardMarkup()
#
#     # Предположим, что функция get_service_detail_by_id возвращает список кортежей (мастер, цена),
#     # соответствующих данному service_id
#     for master_name, price in service_details:
#         button_text = f"{master_name} ({price} руб.)"
#         markup.add(types.InlineKeyboardButton(
#             text=button_text,
#             callback_data=f"master_{master_name}_{price}"
#         ))
#
#     markup.add(types.InlineKeyboardButton("Назад", callback_data="back_to_services"))
#     return markup

# Функция для генерации клавиатуры с мастерами и ценой после спринта
def generate_master_keyboard(service_id):
    service_details = get_service_detail_new(service_id)
    markup = types.InlineKeyboardMarkup()

    for master_name in service_details:
        markup.add(types.InlineKeyboardButton(
            text=master_name,
            callback_data=f"master_{master_name}"
        ))

    markup.add(types.InlineKeyboardButton("Назад", callback_data="back_to_services"))
    return markup


# # Функция для генерации клавиатуры с доступными годами
# def generate_year_keyboard():
#     years = get_unique_active_years(service_master_price_id)
#     markup = types.InlineKeyboardMarkup()
#     for year in years:
#         markup.add(types.InlineKeyboardButton(str(year), callback_data=f"year_{year}"))
#     markup.add(types.InlineKeyboardButton("Назад", callback_data="back_to_masters"))
#     return markup

# Функция для генерации клавиатуры с доступными годами
def generate_year_keyboard(telegram_id):

    # Извлекаем записи для данного telegram_id
    records = data_storage.get(telegram_id, [])

    if not records:
        return None  # Или другой способ обработки отсутствия записей

    # Берем первый элемент списка и извлекаем service_master_price_id
    service_master_price_id = records[0].get('service_master_price_id')

    if not service_master_price_id:
        return None  # Или другой способ обработки отсутствия service_master_price_id

    # Получаем уникальные доступные годы с учетом service_master_price_id
    years = get_unique_active_years_new(service_master_price_id)

    if not years:
        return None  # Или другой способ обработки отсутствия подходящих годов

    # Генерация клавиатуры
    markup = types.InlineKeyboardMarkup()
    for year in years:
        markup.add(types.InlineKeyboardButton(str(year), callback_data=f"year_{year}"))
    markup.add(types.InlineKeyboardButton("Назад", callback_data="back_to_masters"))
    return markup


# # Функция для генерации клавиатуры с доступными месяцами
# def generate_month_keyboard(telegram_id, year):
#     months = get_unique_months_in_year(telegram_id,year)
#     markup = types.InlineKeyboardMarkup()
#     for month in months:
#         markup.add(types.InlineKeyboardButton(month_to_str(month), callback_data=f"month_{month}_{year}"))
#     markup.add(types.InlineKeyboardButton("Назад", callback_data="back_to_years"))
#     return markup



# Функция для генерации клавиатуры с доступными месяцами
def generate_month_keyboard(telegram_id, year):
    # Извлекаем записи для данного telegram_id
    records = data_storage.get(telegram_id, [])

    if not records:
        return None  # Или другой способ обработки отсутствия записей

    # Берем первый элемент списка и извлекаем service_master_price_id
    service_master_price_id = records[0].get('service_master_price_id')

    if not service_master_price_id:
        return None  # Или другой способ обработки отсутствия service_master_price_id

    # Получаем уникальные доступные месяцы с учетом service_master_price_id
    months = get_unique_months_in_year_new(service_master_price_id, year)

    if not months:
        return None  # Или другой способ обработки отсутствия подходящих месяцев

    # Генерация клавиатуры
    markup = types.InlineKeyboardMarkup()
    for month in months:
        markup.add(types.InlineKeyboardButton(month_to_str(month), callback_data=f"month_{month}_{year}"))
    markup.add(types.InlineKeyboardButton("Назад", callback_data="back_to_years"))
    return markup




# Вспомогательная функция для преобразования численного представления месяца в строку
def month_to_str(month_number):
    months = {
        1: "Январь",
        2: "Февраль",
        3: "Март",
        4: "Апрель",
        5: "Май",
        6: "Июнь",
        7: "Июль",
        8: "Август",
        9: "Сентябрь",
        10: "Октябрь",
        11: "Ноябрь",
        12: "Декабрь"
    }
    return months[month_number]

# # Функция для генерации клавиатуры с доступными днями
# def generate_day_keyboard(telegram_id, year, month):
#     """ Генерирует клавиатуру с днями выбранного месяца, где доступны только указанные даты. :param year: Год. :param month: Месяц. :return: Объект InlineKeyboardMarkup с клавиатурой. """
#     # Получение доступных дат из базы данных
#     available_days = get_unique_days_in_month_and_year(service_master_price_id, year, month)
#
#     # Получаем количество дней в месяце и первый день недели
#     days_in_month = calendar.monthrange(year, month)[1]
#     first_weekday = calendar.monthrange(year, month)[0]
#
#     keyboard = []
#     weekdays_row = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
#     keyboard.append(
#         [InlineKeyboardButton(text=weekday, callback_data="none") for weekday in weekdays_row]
#     )
#
#     row = []
#     # Добавляем пустые кнопки для выравнивания первой недели
#     for _ in range(first_weekday):
#         row.append(InlineKeyboardButton(text=" ", callback_data="none"))
#
#     # Заполняем дни месяца
#     for day in range(1, days_in_month + 1):
#         if day in available_days:
#             text = f"{day}"
#             callback_data = str(datetime(year, month, day).date())
#         else:
#             text = " "
#             callback_data = "none"
#
#         button = InlineKeyboardButton(text=text, callback_data=callback_data)
#         row.append(button)
#
#         # Перенос на новую строку после каждой недели
#         if (day + first_weekday) % 7 == 0:
#             keyboard.append(row)
#             row = []
#
#     # Если последний день месяца не завершает неделю, добавляем пустые кнопки
#     remaining_days = (days_in_month + first_weekday) % 7
#     if remaining_days != 0:
#         for _ in range(7 - remaining_days):
#             row.append(InlineKeyboardButton(text=" ", callback_data="none"))
#         keyboard.append(row)
#
#     # Добавление кнопки "Назад"
#     back_button = [InlineKeyboardButton(text="Назад", callback_data=f"back|{year}|{month}")]
#     keyboard.append(back_button)
#
#     return InlineKeyboardMarkup(keyboard)



# Функция для генерации клавиатуры с доступными днями
def generate_day_keyboard(telegram_id, year, month):
    # Извлекаем записи для данного telegram_id
    records = data_storage.get(telegram_id, [])

    if not records:
        return None  # Или другой способ обработки отсутствия записей

    # Берем первый элемент списка и извлекаем service_master_price_id
    service_master_price_id = records[0].get('service_master_price_id')

    if not service_master_price_id:
        return None  # Или другой способ обработки отсутствия service_master_price_id

    # Получаем уникальные доступные дни с учетом service_master_price_id
    available_days = get_unique_days_in_month_and_year_new(service_master_price_id, year, month)
    print(available_days)
    print(service_master_price_id)
    print(year)
    print(month)

    # Получаем количество дней в месяце и первый день недели
    days_in_month = calendar.monthrange(year, month)[1]
    first_weekday = calendar.monthrange(year, month)[0]

    keyboard = []
    weekdays_row = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    keyboard.append([InlineKeyboardButton(text=weekday, callback_data="none") for weekday in weekdays_row])

    row = []
    # Добавляем пустые кнопки для выравнивания первой недели
    for _ in range(first_weekday):
        row.append(InlineKeyboardButton(text=" ", callback_data="none"))

    # Заполняем дни месяца
    for day in range(1, days_in_month + 1):
        if day in available_days:
            text = f"{day:02}"  # Преобразование числа в строку с ведущим нулем
            callback_data = str(datetime(year, month, day).date())
        else:
            text = " "
            callback_data = "none"

        button = InlineKeyboardButton(text=text, callback_data=callback_data)
        row.append(button)

        # Перенос на новую строку после каждой недели
        if (day + first_weekday) % 7 == 0:
            keyboard.append(row)
            row = []

    # Если последний день месяца не завершает неделю, добавляем пустые кнопки
    remaining_days = (days_in_month + first_weekday) % 7
    if remaining_days != 0:
        for _ in range(7 - remaining_days):
            row.append(InlineKeyboardButton(text=" ", callback_data="none"))
        keyboard.append(row)

    # Добавление кнопки "Назад"
    back_button = [InlineKeyboardButton(text="Назад", callback_data=f"back|{year}|{month:02}")]  # Также преобразуем месяц в строку с ведущим нулем
    keyboard.append(back_button)

    return InlineKeyboardMarkup(keyboard)





# Генерация клавиатуры с временными интервалами
def generate_time_keyboard(appointment_date):
    available_times = get_available_times_for_date(appointment_date)

    keyboard = []
    for time_slot in available_times:
        button = InlineKeyboardButton(text=time_slot, callback_data=time_slot)
        keyboard.append([button])

    # Добавление кнопки "Назад"
    back_button = [InlineKeyboardButton(text="Назад", callback_data="back_to_days")]
    keyboard.append(back_button)

    return InlineKeyboardMarkup(keyboard)



def format_date(year, month, day):
    return f'{day}.{month}.{year}'

def generate_confirmation_message(user_id, appointment_date, appointment_time):
    client_id = data_storage[user_id][0]['client_id']
    user_info = get_user_info_by_id(client_id)
    name = user_info['name']
    phone_number = user_info['phone_number']
    service_master_price_id = data_storage[user_id][0]['service_master_price_id']
    service_info = get_service_info_by_service_master_price_id(service_master_price_id)
    service_name = service_info['service_name']
    master_name = service_info['name']
    price = service_info['price']

    formatted_date = format_date(*appointment_date.split('-'))

    text = (
        f"Пожалуйста, подтвердите запись и проверьте корректность Ваших данных:"
        f"\nДата: {formatted_date}\nВремя: {appointment_time}\nМастер: {master_name}\nУслуга: {service_name}\nСтоимость: {price}₽\nВаше имя: {name}\nВаш номер телефона: {phone_number}"
    )
    keyboard = InlineKeyboardMarkup()
    confirm_button = InlineKeyboardButton(text="Подтвердить", callback_data=f"confirm_{user_id}")
    cancel_button = InlineKeyboardButton(text="Отменить", callback_data=f"cancel_{user_id}")
    edit_info_button = InlineKeyboardButton(text="Изменить информацию о себе", callback_data=f"edit_info_{user_id}")
    keyboard.row(confirm_button, cancel_button)
    keyboard.add(edit_info_button)
    return text, keyboard


# Функция для генерации пустого макета
def generate_empty_layout():
    return "", ReplyKeyboardRemove()



# # Обработчик нажатия кнопок каталога услуг
# @bot.callback_query_handler(func=lambda call: call.data.startswith('service_'))
# def handle_service_selection(call):
#     service_name = call.data.split('_')[1]
#     bot.edit_message_text(f"Вы выбрали услугу: {service_name}. Выберите мастера:", call.message.chat.id,
#                           call.message.message_id, reply_markup=generate_master_keyboard(service_name))
#
#
# # Обработчик нажатия кнопок мастеров
# @bot.callback_query_handler(func=lambda call: call.data.startswith('master_'))
# def process_master(call):
#     _, master, price = call.data.split("_")
#     bot.answer_callback_query(call.id, f"Вы выбрали {master}, цена: {price} руб.")


# Обработчик нажатия кнопок каталога услуг
@bot.callback_query_handler(func=lambda call: call.data.startswith('service_'))
def handle_service_selection(call):
    user_id = call.message.chat.id
    service_id = int(call.data.split('_')[1])
    user_selected_services[user_id] = service_id  # Сохраняем id услуги для данного пользователя
    bot.edit_message_text(
        "Выберите мастера:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=generate_master_keyboard(service_id)
    )







# Обработчик нажатия кнопок мастеров
@bot.callback_query_handler(func=lambda call: call.data.startswith('master_'))
def process_master(call):
    _, master = call.data.split("_")
    user_id = call.message.chat.id
    if user_id in user_selected_services:
        service_id = user_selected_services.get(user_id)
        service_master_price_id = get_service_master_price_id(service_id, master)
        telegram_id = call.message.chat.id

        print(service_master_price_id)

        # Проверка, есть ли записи для данного пользователя
        if telegram_id not in data_storage:
            data_storage[telegram_id] = []

        # Поиск записи с текущим telegram_id
        found_index = None
        for index, record in enumerate(data_storage[telegram_id]):
            if record['telegram_id'] == telegram_id:
                found_index = index
                break

        # Если запись найдена, обновляем её
        if found_index is not None:
            data_storage[telegram_id][found_index]['service_master_price_id'] = service_master_price_id
        else:
            # Если запись не найдена, добавляем новую
            data_storage[telegram_id].append({
                "service_master_price_id": service_master_price_id,
                "telegram_id": telegram_id
            })

        # Вывод данных в консоль
        pprint.pprint(data_storage)

        bot.edit_message_text(
            "Выберите год:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=generate_year_keyboard(telegram_id)
        )
    else:
        bot.answer_callback_query(call.id, "Произошла ошибка. Попробуйте выбрать услугу заново.")



#Обработчик нажатия кнопок года
@bot.callback_query_handler(func=lambda call: call.data.startswith('year_'))
def handle_year_selection(call):
    year = call.data.split('_')[1]
    bot.edit_message_text(
        f"Вы выбрали год: {year}",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=generate_month_keyboard(call.message.chat.id, int(year)))

#Обработчик нажатия кнопок месяца
@bot.callback_query_handler(func=lambda call: call.data.startswith('month_'))
def handle_month_selection(call):
    _, month, year = call.data.split('_')
    bot.edit_message_text(
        f"Вы выбрали месяц: {month_to_str(int(month))} {year}",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=generate_day_keyboard(call.message.chat.id, int(year), int(month)))




# Обработчик нажатия кнопок дней
@bot.callback_query_handler(func=lambda call: re.match(r'\d{4}-\d{2}-\d{2}', call.data))
def select_date(call):
    selected_date = call.data
    chat_id = call.message.chat.id
    user_id = call.from_user.id

    # Сохраняем текущий выбор года и месяца в словаре
    user_dates[user_id] = {
        'year': int(selected_date[:4]),
        'month': int(selected_date[5:7]),
        'day': int(selected_date[8:])
    }

    bot.edit_message_text(
        f"Выберите время {selected_date}:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=generate_time_keyboard(selected_date)
    )

# Обработчик нажатия кнопок времени
@bot.callback_query_handler(func=lambda call: re.match(r'\d{2}:\d{2}', call.data))
def select_time(call):
    selected_time = call.data
    chat_id = call.message.chat.id
    user_id = call.from_user.id

    # Вывод данных в консоль
    pprint.pprint(data_storage)

    # Формируем полную дату из года, месяца и дня
    date_parts = [str(user_dates[user_id]['year']), str(user_dates[user_id]['month']).zfill(2),
                  str(user_dates[user_id]['day']).zfill(2)]
    appointment_date = '-'.join(date_parts)

    # Проверка, есть ли записи для данного пользователя
    if user_id not in data_storage:
        data_storage[user_id] = []

    # Поиск записи с текущим telegram_id
    found_index = None
    for index, record in enumerate(data_storage[user_id]):
        if record['telegram_id'] == user_id:
            found_index = index
            break

    # Если запись найдена, обновляем её
    if found_index is not None:
        data_storage[user_id][found_index]['appointment_date'] = appointment_date
        data_storage[user_id][found_index]['appointment_time'] = selected_time
    else:
        # Если запись не найдена, добавляем новую
        data_storage[user_id].append({
            "appointment_date": appointment_date,
            "appointment_time": selected_time,
            "telegram_id": user_id
        })

    # Проверяем, есть ли пользователь в базе данных
    if not is_user_in_database(user_id):
        bot.send_message(chat_id, "Кажется, вы еще не зарегистрированы. Пожалуйста, введите ваше имя:")
        bot.register_next_step_handler_by_chat_id(chat_id, handle_name_input)

        # Вывод данных в консоль
        pprint.pprint(data_storage)
    else:
        # Получаем client_id через функцию get_user_id_by_telegram_id
        client_id = get_user_id_by_telegram_id(user_id)

        # Если запись найдена, обновляем её
        if found_index is not None:
            data_storage[user_id][found_index]['client_id'] = client_id
        else:
            # Если запись не найдена, добавляем новую
            data_storage[user_id].append({
                "appointment_date": appointment_date,
                "appointment_time": selected_time,
                "telegram_id": user_id,
                "client_id": client_id
            })

        # Генерируем сообщение с подтверждением записи
        confirmation_text, confirmation_keyboard = generate_confirmation_message(
            user_id, appointment_date, selected_time
        )

        # Отправляем сообщение с подтверждением
        bot.edit_message_text(
            text=confirmation_text,
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=confirmation_keyboard
        )

        # Вывод данных в консоль
        pprint.pprint(data_storage)





# Обработчик нажатия кнопки подтверждения
@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def confirm_appointment(call):
    user_id = int(call.data.split("_")[1])
    chat_id = call.message.chat.id

    # Находим запись в data_storage
    found_record = next((record for record in data_storage[user_id] if record['telegram_id'] == user_id), None)

    if found_record:
        # Подтверждение записи
        appointment_date = found_record['appointment_date']
        appointment_time = found_record['appointment_time']
        service_master_price_id = found_record['service_master_price_id']
        client_id = found_record.get('client_id')

        # Получаем appointments_id
        appointments_id = get_appointment_id_by_params(appointment_date, appointment_time, service_master_price_id)

        if appointments_id != "Назначение не найдено.":
            # Выводим данные в консоль
            print(f"appointments_id: {appointments_id}, appointment_date: {appointment_date}, "
                  f"appointment_time: {appointment_time}, service_master_price_id: {service_master_price_id}, "
                  f"client_id: {client_id}")

            update_client_id_in_appointment(appointments_id, client_id, service_master_price_id)

            # Логика завершения записи
            final_message = f"Ваша запись на {appointment_date} в {appointment_time} подтверждена!"
            bot.edit_message_text(final_message, chat_id, call.message.message_id)
            bot.edit_message_text("Благодарим, Вас!", call.message.chat.id, call.message.message_id, reply_markup=None)
            bot.send_message(call.message.chat.id, "Возврат в главное меню", reply_markup=main_panel(call.from_user.id))
            bot.register_next_step_handler(call.message, on_click)

            # Очистка временной информации
            del user_dates[user_id]
        else:
            bot.answer_callback_query(call.id, "Не удалось найти подходящее назначение.", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "Ошибка подтверждения записи.", show_alert=True)




# Обработчик нажатия на кнопку "Изменить информацию о себе"
@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_info_'))
def handle_edit_info(call):
    user_id = int(re.search(r'\d+', call.data).group())
    chat_id = call.message.chat.id

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Пожалуйста, введите ваше имя:",
        parse_mode='HTML'
    )

    bot.register_next_step_handler_by_chat_id(chat_id, handle_name_input_rename)

# Обработчик ввода имени
def handle_name_input_rename(message):
    name = message.text.strip()
    chat_id = message.chat.id

    # Валидируем имя
    if not is_valid_name(name):
        bot.send_message(chat_id, "Имя должно содержать только буквы кириллицы. Пожалуйста, попробуйте снова:")
        bot.register_next_step_handler_by_chat_id(chat_id, handle_name_input_rename)
        return

    # Запрос номера телефона
    bot.send_message(chat_id, "Пожалуйста, введите ваш номер телефона:")
    bot.register_next_step_handler_by_chat_id(chat_id, handle_phone_input_rename, name=name)

# Обработчик ввода номера телефона
def handle_phone_input_rename(message, name):
    phone_number = message.text.strip()
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not is_valid_phone_number(phone_number):
        bot.send_message(chat_id, "Номер телефона введен неверно. Пожалуйста, попробуйте снова:")
        bot.register_next_step_handler_by_chat_id(chat_id, handle_phone_input_rename, name=name)
        return

    # Логика изменения имени и номера телефона пользователя в базе данных
    rename_user_info(user_id, name, phone_number)

    # После успешного сохранения получаем client_id
    client_id = get_user_id_by_telegram_id(user_id)

    # Вносим client_id в словарь data_storage
    if user_id not in data_storage:
        data_storage[user_id] = [{"client_id": client_id}]
    else:
        # Если запись уже существует, обновляем client_id во всех записях
        for entry in data_storage[user_id]:
            entry["client_id"] = client_id

    bot.send_message(chat_id, f"Спасибо, {name}, ваш профиль успешно создан!")

    # Генерируем сообщение с подтверждением записи
    confirmation_text, confirmation_keyboard = generate_confirmation_message(
        user_id, data_storage[user_id][0]['appointment_date'], data_storage[user_id][0]['appointment_time']
    )

    # Отправляем сообщение с подтверждением
    bot.send_message(chat_id, confirmation_text, reply_markup=confirmation_keyboard)

    # Вывод данных в консоль
    pprint.pprint(data_storage)



# Обработчик нажатия кнопки отмены
@bot.callback_query_handler(func=lambda call: call.data.startswith("cancel_"))
def cancel_appointment(call):
    user_id = int(call.data.split("_")[1])
    chat_id = call.message.chat.id

    # Отмена записи
    bot.edit_message_text("Выбор отменен.", call.message.chat.id, call.message.message_id, reply_markup=None)
    bot.send_message(call.message.chat.id, "Что-то еще?", reply_markup=main_panel(call.from_user.id))
    bot.register_next_step_handler(call.message, on_click)

    # Очистка временной информации
    del user_dates[user_id]







# Обработчик ввода имени пользователя
def handle_name_input(message):
    name = message.text.strip()
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Генерируем пустой макет
    empty_text, empty_keyboard = generate_empty_layout()

    if not is_valid_name(name):
        bot.send_message(chat_id, "Имя должно содержать только буквы кириллицы. Пожалуйста, попробуйте снова:")
        bot.register_next_step_handler_by_chat_id(chat_id, handle_name_input)
        return

    # Запрашиваем номер телефона
    bot.send_message(chat_id, "Пожалуйста, введите ваш номер телефона:")
    bot.register_next_step_handler_by_chat_id(chat_id, handle_phone_input, name=name)



# Обработчик ввода номера телефона
def handle_phone_input(message, name):
    phone_number = message.text.strip()
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not is_valid_phone_number(phone_number):
        bot.send_message(chat_id, "Номер телефона введен неверно. Пожалуйста, попробуйте снова:")
        bot.register_next_step_handler_by_chat_id(chat_id, handle_phone_input, name=name)
        return

    # Логика сохранения имени и номера телефона пользователя в базу данных
    save_user_to_database(user_id, name, phone_number)

    # После успешного сохранения получаем client_id
    client_id = get_user_id_by_telegram_id(user_id)

    # Вносим client_id в словарь data_storage
    if user_id not in data_storage:
        data_storage[user_id] = [{"client_id": client_id}]
    else:
        # Если запись уже существует, обновляем client_id во всех записях
        for entry in data_storage[user_id]:
            entry["client_id"] = client_id

    bot.send_message(chat_id, f"Спасибо, {name}, ваш профиль успешно создан!")

    # Генерируем сообщение с подтверждением записи
    confirmation_text, confirmation_keyboard = generate_confirmation_message(
        user_id, data_storage[user_id][0]['appointment_date'], data_storage[user_id][0]['appointment_time']
    )

    # Отправляем сообщение с подтверждением
    bot.send_message(chat_id, confirmation_text, reply_markup=confirmation_keyboard)

    # Вывод данных в консоль
    pprint.pprint(data_storage)





# Функция для проверки имени
def is_valid_name(name):
    # Регулярное выражение для проверки кириллицы и отсутствия цифр
    pattern = r'^[\u0400-\u04FF]+$'
    return bool(re.fullmatch(pattern, name))





# Обработчик нажатия кнопки "Назад" в списке времени
@bot.callback_query_handler(func=lambda call: call.data == "back_to_days")
def back_to_days(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id

    if user_id not in user_dates:
        bot.answer_callback_query(call.id, "Ошибка! Попробуйте начать заново.")
        return

    year = user_dates[user_id]['year']
    month = user_dates[user_id]['month']

    bot.edit_message_text(
        f"Выберите день в {month}/{year}:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=generate_day_keyboard(call.message.chat.id, year, month)
    )


# Обработчик нажатия кнопки "Назад" в списке дней
@bot.callback_query_handler(func=lambda call: 'back|' in call.data)
def back_to_months(call):
    _, year, month = call.data.split('|')
    telegram_id = call.message.chat.id
    bot.edit_message_text(
        f"Выберите месяц в {year} году:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=generate_month_keyboard(telegram_id, int(year))
    )


# Обработчик нажатия кнопки "Назад" в списке месяцев
@bot.callback_query_handler(func=lambda call: call.data == 'back_to_years')
def back_to_years(call):
    telegram_id = call.from_user.id
    bot.edit_message_text(
        "Выберите год:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=generate_year_keyboard(telegram_id)
    )



# Обработчик нажатия кнопки "Назад" в списке годов
@bot.callback_query_handler(func=lambda call: call.data == 'back_to_masters')
def back_to_masters(call):
    service_id = user_selected_services[call.message.chat.id]
    bot.edit_message_text(
        "Выберите мастера:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=generate_master_keyboard(service_id)
    )







# # Обработчик нажатия кнопки "Назад" в списке мастеров
# @bot.callback_query_handler(func=lambda call: call.data == 'back_to_services')
# def back_to_services(call):
#     bot.edit_message_text("Выберите услугу:", call.message.chat.id, call.message.message_id,
#                           reply_markup=generate_service_keyboard())

# Обработчик нажатия кнопки "Назад" в списке мастеров
@bot.callback_query_handler(func=lambda call: call.data == 'back_to_services')
def back_to_services(call):
    bot.clear_step_handler_by_chat_id(call.message.chat.id)
    bot.edit_message_text("Выберите услугу:", call.message.chat.id, call.message.message_id,
                         reply_markup=generate_service_keyboard())






# Обработчик нажатия кнопки "Отмена"
@bot.callback_query_handler(func=lambda call: call.data == 'cancel')
def cancel_selection(call):
    bot.edit_message_text("Выбор отменен.", call.message.chat.id, call.message.message_id, reply_markup=None)
    bot.send_message(call.message.chat.id, "Что-то еще?", reply_markup=main_panel(call.from_user.id))
    bot.register_next_step_handler(call.message, on_click)



#Временное хранение услуги
from collections import defaultdict

# Словарь для хранения идентификаторов выбранных услуг по пользователям
user_selected_services = defaultdict(lambda: None)

# Словарь для хранения выбранной даты
chat_data = defaultdict(dict)


# Словарь для хранения данных о пользователе
user_dates = {}

# Глобальная переменная для хранения данных
data_storage: Dict[int, List[Dict[str, str]]] = {}


def extract_and_get_appointment_id(data_storage, key):
    for entry in data_storage[key]:
        appointment_date = entry["appointment_date"]
        appointment_time = entry["appointment_time"]
        service_master_price_id = entry["service_master_price_id"]

        # Получаем appointments_id
        appointments_id = get_appointment_id_by_params(appointment_date, appointment_time,
                                                       service_master_price_id)

        return appointments_id
    return "Нет подходящих записей."

def extract_client_id_from_data_storage(data_storage, key):
    try:
        return data_storage[key][0]['client_id']
    except (KeyError, IndexError):
        return None


########################################################
# Занесение расписания работы - начало

# Шаг 1 - показываем месяца
def show_month(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Выберите месяц для создания окон", reply_markup=create_month_keyboard(""))

# Шаг 2 - показываем мастеров
def show_masters(message, y, m):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Выберите мастера:", reply_markup=create_masters_keyboard(y, m))

# Шаг 3 - показываем опции
def show_options(message, name_m, id_m, y, m):
    chat_id = message.chat.id
    bot.send_message(chat_id, f"Мастер {name_m}\nВы можете занести стандартное расписание с ПН по ПТ с 9:00 по 18:00 \n "
                     , reply_markup=create_options_keyboard(name_m, id_m, y, m))

#Нажатие на кнопку месяца
@bot.callback_query_handler(func=lambda call: call.data.startswith("schMonth_"))
def handle_month_selection(call):
    _, date_string = call.data.split('_')  # Распаковка данных
    y, m = date_string.split('-')  # Разделяем на год и месяц
    show_masters(call.message, y, m)

#Нажатие на мастера
@bot.callback_query_handler(func=lambda call: call.data.startswith("schMaster_"))
def handle_master_selection(call):
    _, id_master, name_m, y, m = call.data.split('_')  # Распаковка данных
    show_options(call.message, name_m, id_master, y, m)

#Нажатие на опцию
@bot.callback_query_handler(func=lambda call: call.data.startswith("opt_"))
def handle_opt_selection(call):
    _, opt, id_master, name_m, y, m = call.data.split('_')  # Распаковка данных
    if int(opt) == 1 :
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton(text="Назад", callback_data="shStep_3_"+y+"_"+m+"_"+id_master+"_"+name_m))
        markup.add(types.InlineKeyboardButton(text="В главное меню", callback_data="main"))
        # проверяем что на этот месяц не созданы все стандартные окна
        res = check_all_default_slots_for_master(id_master, y, m)
        if len(res) == 0:
            create_appointments_default(id_master, y, m)
            bot.send_message(call.message.chat.id, f"Cтандартные окна для мастера {name_m} созданы", reply_markup=markup)
        else:
            bot.send_message(call.message.chat.id, f"Все стандартные окна для мастера {name_m} уже созданы", reply_markup=markup)

#Возврат к предыдущему шагу
@bot.callback_query_handler(func=lambda call: call.data.startswith("shStep_"))
def handle_return_selection(call):
    parts = call.data.split('_')  # Распаковка данных
    #на первом шаге данных нет
    if int(parts[1]) == 1:
        show_month(call.message)
    #на втором год и мясц
    if int(parts[1]) == 2:
        y=parts[2]
        m=parts[3]
        show_masters(call.message, y, m)
    #на третьем месяц год id мастера и имя мастера
    if int(parts[1]) == 3:
        y = parts[2]
        m = parts[3]
        id_m = parts[4]
        name_m = parts[5]
        show_options(call.message, name_m, id_m, y, m)

# Функция для создания клавиатуры с месяцами
def create_month_keyboard(prefix):
    markup = types.InlineKeyboardMarkup()
    today = date.today()

    for i in range(6):  # Текущий месяц + 5
        future_date = today + timedelta(days=i * 30)  # Упрощение, 30 дней на месяц
        month_name = month_to_str(future_date.month) + " "+ future_date.strftime("%Y")  # Название месяца и год, например: "November 2024"
        month_data = future_date.strftime("%Y") + "-" + str(future_date.month)  # Данные для callback, например: "2024-11"

        markup.add(types.InlineKeyboardButton(month_name, callback_data=f"{prefix}schMonth_{month_data}"))
    markup.add(types.InlineKeyboardButton(text="В главное меню", callback_data="main"))
    return markup

# Функция для создания клавиатуры с мастерами
def create_masters_keyboard(y, m):
    markup = InlineKeyboardMarkup()
    masters = get_masters()
    for master in masters:
        master_btn = InlineKeyboardButton(text=master[1], callback_data="schMaster_" + str(master[0]) + "_" + str(master[1]) + "_" + y + "_" + m)
        markup.add(master_btn)
    markup.add(types.InlineKeyboardButton(text="В главное меню", callback_data="main"))
    markup.add(types.InlineKeyboardButton(text="Назад", callback_data="shStep_1"))
    return markup

# Функция для создания клавиатуры с опциями
def create_options_keyboard(name_m, id_m, y, m):
    markup = InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="Стандартное расписание", callback_data="opt_1_"+id_m+"_"+name_m+"_"+ y + "_" + m))
    markup.add(types.InlineKeyboardButton(text="В главное меню", callback_data="main"))
    markup.add(types.InlineKeyboardButton(text="Назад", callback_data="shStep_2_"+y+"_"+m))
    return markup

# Функция для добавления в бд стандартного расписания на месяц
def create_appointments_default(id_master, y, m):
    dates = get_weekdays_in_month(int(y), int(m))
    for d in dates:
        for app in apps:
            add_appointments(d, app, id_master)

# Функция получения будних дней месяца
def get_weekdays_in_month(y, m):
    # Получаем количество дней в месяце
    days_in_month = calendar.monthrange(y, m)[1]
    weekdays = []

    for d in range(1, days_in_month + 1):
        # Получаем день недели (0 - понедельник, 6 - воскресенье)
        day_of_week = calendar.weekday(y, m, d)
        # Добавляем только будние дни (не субботу и воскресенье)
        if day_of_week < 5:  # Понедельник (0) - Пятница (4)
            weekdays.append(f"{y}-{m:02d}-{d:02d}")

    return weekdays

# Функция получения  дней месяца
def get_dates_in_month(y, m):
    # Получаем количество дней в месяце
    days_in_month = calendar.monthrange(y, m)[1]
    # Генерируем список всех дат в формате 'YYYY-MM-DD'
    dates = [f"{y}-{m:02d}-{day:02d}" for day in range(1, days_in_month + 1)]
    return dates

# Проверка создания всех стандартных окон
def check_all_default_slots_for_master(id_master, y, m):
    # Получаем все рабочие дни месяца для мастера
    weekdays = get_weekdays_in_month(int(y), int(m))
    # Структура для хранения свободных слотов
    free_days = {}
    for d in weekdays:
        free_app = []
        for app in apps:
            res = get_appointments(id_master, d, app)
            if res:
                free_app.append(app)
        if free_app:
            free_days[d] = free_app
    return free_days

# Занесение расписания работы - конец
########################################################



# Занесение расписания работы - конец
########################################################

########################################################
# Отправка клиентам уведомления об открытии записи - начало
#Шаг 1 - выбор месяца
def send_notification_client(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "На какой месяц открылась запись?", reply_markup=create_month_keyboard("ntf"))

#Шаг 2 - Получаем id клиентов и отправляем каждому сообщение
def get_ids_and_send(message, y, m):
    chat_id = message.chat.id
    name_month = month_to_str(m)
    text = f"Уважаемые клиенты!\nСообщаем, что запись на {name_month} {y} открыта.\nС любовью, ваша студия Nailove <3"
    ids = get_user_telegram_ids()
    count_error = 0
    if ids:
        for i in ids:
            try:
                bot.send_message(chat_id=i, text=text)
                print(f"Сообщение успешно отправлено!{i}")
            except telebot.apihelper.ApiTelegramException as e:
                print(f"Ошибка при отправке сообщения {i}: {e}")
                count_error+=1
    else:
        count_error+=1

    markup = InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="В главное меню", callback_data="main"))
    if count_error == 0:
        bot.send_message(chat_id, f"Уведомления об открытии записи на {name_month} {y} успешно отправлены", reply_markup=markup)
    else:
        bot.send_message(chat_id, "Произошла ошибка. Обратитесь к разработчику.", reply_markup=markup)


#Нажатие на кнопку месяца
@bot.callback_query_handler(func=lambda call: call.data.startswith("ntfschMonth_"))
def handle_month_ntf_selection(call):
    _, date_string = call.data.split('_')  # Распаковка данных
    y, m = date_string.split('-')  # Разделяем на год и месяц
    #проверим что на этот месяц есть хотя бы одно свободное окно
    res = check_free_app_for_month_year(int(m), int(y))
    if res:
        get_ids_and_send(call.message, int(y), int(m))
    else:
        bot.send_message(call.message.chat.id, "На данный месяц нет ни одного свободного окна. Выберите другой")

# Отправка клиентам уведомления об открытии записи - конец
########################################################







########################################################
# Создание новых услуг со стоимостью - костыль
#  /new_service
@bot.message_handler(commands=['new_service'])
def new_service(message):
    add_service('Маникюр хитрый', 'Подпил, покраска, а стоит дороже', '2000 руб.')


# Создание новой cтоимости услуги мастеров без стоимости - костыль
#  /new_smp
@bot.message_handler(commands=['new_smp'])
def new_service_master_price(message):
    add_service_master_price(1, 1)

#

