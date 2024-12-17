import sqlite3

DB_NEW = 'nailBD_1_9.sql'

# подключение БД и создание её
def init_db():
    conn = sqlite3.connect(DB_NEW)
    # Активируем поддержку внешних ключей
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    # Создание таблиц
    # Роли
    cur.execute('''
    CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role_name TEXT NOT NULL UNIQUE
    )
    ''')
    # Пользователи
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone_number TEXT NOT NULL,
        role_id INTEGER,
        telegram_id INTEGER UNIQUE NOT NULL,
        FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE SET NULL
    )
    ''')

    # Изменение спринта: переместила в таблицу услуг стоимость
    # Услуги
    cur.execute(
        ''' CREATE TABLE IF NOT EXISTS services ( 
        service_id INTEGER PRIMARY KEY  AUTOINCREMENT NOT NULL UNIQUE, 
        service_name TEXT NOT NULL, 
        description TEXT NOT NULL,
        price TEXT NOT NULL) 
        ''')

    # Изменение спринта: убрала из таблицы стоимость
    # Стоимость услуги мастеров
    cur.execute(
        ''' CREATE TABLE IF NOT EXISTS service_master_price ( 
         service_master_price_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
         service_id INTEGER NOT NULL,
         master_id INTEGER NOT NULL,
         FOREIGN KEY (service_id) REFERENCES services (service_id) ON DELETE CASCADE,
         FOREIGN KEY (master_id) REFERENCES users (id) ON DELETE CASCADE
        ) 
        ''')

    # Изменение спринта: тут теперь  service_master_price_id может быть пустым, а так же добавлено поле master_id
    # Записи
    cur.execute(
        ''' CREATE TABLE IF NOT EXISTS appointments ( 
        appointments_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, 
        appointment_date TEXT NOT NULL,
        appointment_time TEXT NOT NULL,
        service_master_price_id INTEGER,
        client_id INTEGER,
        master_id INTEGER NOT NULL,
        IsActive INTEGER NOT NULL CHECK(IsActive IN (0, 1)),
        FOREIGN KEY (service_master_price_id) REFERENCES service_master_price (service_master_price_id) ON DELETE CASCADE,
        FOREIGN KEY (client_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (master_id) REFERENCES users (id) ON DELETE CASCADE
        ) 
        ''')


    # Проверка на существование ролей
    cur.execute("SELECT COUNT(*) FROM roles")
    role_count = cur.fetchone()[0]

    # Если таблица ролей пуста, добавляем начальные роли
    if role_count == 0:
        roles = [("Admin",), ("User",), ("Master",)]
        cur.executemany("INSERT INTO roles (role_name) VALUES (?)", roles)
        print("Роли успешно добавлены")
    else:
        print("Роли уже существуют в базе данных")
    conn.commit()
    cur.close()
    conn.close()
    #просмотр содержания таблицы users
    a('users')
    # просмотр содержания таблицы roles
    a('roles')
    # просмотр содержания таблицы services
    a('services')
    # просмотр содержания таблицы service_master_price
    a('service_master_price')
    # просмотр содержания таблицы appointments
    a('appointments')


#посмотреть содержание таблиц
def a(table_name):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()

    # Выполняем запрос на выбор всех данных из таблицы
    cursor.execute(f"SELECT * FROM {table_name}")

    # Получаем названия столбцов таблицы
    columns = [description[0] for description in cursor.description]
    print(f"Содержимое таблицы {table_name}:")
    print(columns)

    # Выводим каждую строку таблицы
    for row in cursor.fetchall():
        print(row)

    # Закрываем соединение
    conn.close()

def add_admin(name, phone, tele_id):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (name, phone_number, role_id, telegram_id) VALUES (?, ?, ?, ?)",
        (name, phone, 1, tele_id)
    )
    conn.commit()
    conn.close()

# Добавление мастера
def add_master(name, phone, tele_id, serv):
    master_role_id = get_master_role_id()
    if master_role_id is None:
        return "Роль 'Мастер' не найдена. Пожалуйста, добавьте роль в таблицу roles."

    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()

    # Вставляем пользователя с ролью "Мастер"
    cursor.execute(
        "INSERT INTO users (name, phone_number, role_id, telegram_id) VALUES (?, ?, ?, ?)",
        (name, phone, master_role_id, tele_id)
    )
    master_id = cursor.lastrowid
    conn.commit()
    conn.close()

    if serv:
        for id_serv in serv:
            add_service_master_price(id_serv, master_id)
    return True

# Изменение спринта: стоимость добавили сюда
# Добавление услуги
def add_service(service_name, description, price):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO services (service_name, description, price) VALUES (?, ?, ?)",
        (service_name, description, price)
    )
    conn.commit()
    service_id = cursor.lastrowid
    conn.close()
    return service_id

def edt_service_name(service_id, service_name):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE services SET service_name = ? WHERE service_id = ?",
        (service_name, service_id)
    )
    conn.commit()
    conn.close()

def edt_service_descr(service_id, service_descr):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE services SET description = ? WHERE service_id = ?",
        (service_descr, service_id)
    )
    conn.commit()
    conn.close()

def master_in_serv(service_id, master_id):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT service_master_price_id FROM service_master_price WHERE service_id = ? AND master_id = ?",
        (service_id, master_id)
    )
    master_in = cursor.fetchone()
    conn.close()

    if master_in:
        return True
    else:
        return False

def edt_service_price(service_id, price):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE services SET price = ? WHERE service_id = ?",
        (price, service_id)
    )
    conn.commit()
    conn.close()


# Изменение спринта: стоимость убрали отсюда
# Добавление стоимости услуги мастеров
def add_service_master_price(service_id, master_id):
    conn = sqlite3.connect(DB_NEW)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO service_master_price (service_id, master_id) VALUES (?, ?)",
        (service_id, master_id)
    )
    conn.commit()
    conn.close()

# Изменение спринта: убрали service_master_price_id, добавили id_master
# Добавление свободного окна на мастера дату и время
def add_appointments(appointment_date, appointment_time, id_master):
    conn = sqlite3.connect(DB_NEW)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO appointments (appointment_date, appointment_time, master_id, IsActive) VALUES (?, ?, ?, ?)",
        (appointment_date, appointment_time, id_master, '1')
    )
    conn.commit()
    conn.close()

# проверка существования окна записи для мастера на дату и время
def get_appointments(id_master, appointment_date, appointment_time):
    result = True
    conn = sqlite3.connect(DB_NEW)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    cursor.execute('''
                    SELECT * FROM appointments WHERE master_id = ? AND appointment_date = ? AND appointment_time = ?
                ''', (id_master, appointment_date, appointment_time))
    if not cursor.fetchone():
        result = False
    conn.close()
    return result

def check_free_app_for_month_year(month, year):
    """
    Проверяет, есть ли хотя бы одно свободное окно на указанный месяц и год.
    :param month: месяц в виде числа (1-12)
    :param year: год в виде числа (например, 2024)
    :return: True, если строки есть, иначе False
    """
    try:
        # Подключаемся к базе данных
        conn = sqlite3.connect(DB_NEW)
        cursor = conn.cursor()

        # Форматируем месяц с нулем в начале (например, 01, 02...)
        month_str = f"{month:02d}"

        # SQL-запрос для проверки наличия строк
        cursor.execute(
            "SELECT 1 FROM appointments WHERE appointment_date LIKE ? AND IsActive = 1 LIMIT 1",
            (f"{year}-{month_str}%",)
        )

        # Если результат есть, значит строки найдены
        return cursor.fetchone() is not None

    except sqlite3.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")
        return False
    finally:
        if conn:
            conn.close()





# Функция для проверки, является ли пользователь администратором
def is_admin(telegram_id):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()

    # Получаем id роли "Admin"
    cursor.execute("SELECT id FROM roles WHERE role_name = ?", ("Admin",))
    admin_role_id = cursor.fetchone()

    # Если роль "Admin" существует, проверяем, есть ли пользователь с этой ролью
    if admin_role_id:
        admin_role_id = admin_role_id[0]
        cursor.execute("SELECT * FROM users WHERE telegram_id = ? AND role_id = ?", (telegram_id, admin_role_id))
        user = cursor.fetchone()
        conn.close()
        return user is not None
    else:
        conn.close()
        return False

# Функция для проверки, существует ли роль "Мастер"
def get_master_role_id():
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM roles WHERE role_name = ?", ("Master",))
    master_role_id = cursor.fetchone()
    conn.close()
    return master_role_id[0] if master_role_id else None

def get_services():
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    # Извлекаем все услуги из таблицы services
    cursor.execute("SELECT service_id, service_name FROM services")
    services = cursor.fetchall()
    conn.close()
    return services

def get_serv(serv_id):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    cursor.execute("SELECT description, price FROM services WHERE service_id = ?", (serv_id))

    serv = cursor.fetchone()

    conn.close()
    return serv

def get_serv_master(serv_id):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    cursor.execute("SELECT p.master_id FROM services AS s "
                   "JOIN service_master_price AS p ON s.service_id = p.service_id "
                   "WHERE s.service_id = ?", (serv_id))
    serv_masters = [row[0] for row in cursor]
    conn.close()
    return serv_masters

def get_master(master_id):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM users WHERE id = ?", (master_id))
    master_name = cursor.fetchone()
    conn.close()
    return master_name[0] if master_name else None

def get_masters():
    master_role_id = get_master_role_id()
    if master_role_id is None:
        return "Роль 'Мастер' не найдена. Пожалуйста, добавьте роль в таблицу roles."

    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE role_id = (SELECT id FROM roles WHERE role_name = 'Master')")
    masters = cursor.fetchall()
    conn.close()
    return masters


#чекнуть структуры бд
def check():
    # Подключаемся к базе данных
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()

    # Получаем список таблиц в базе данных
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Таблицы в базе данных:")
    for table in tables:
        print(table[0])

    # Проверка структуры таблицы roles
    print("\nСтруктура таблицы roles:")
    cursor.execute("PRAGMA table_info(roles)")
    for column in cursor.fetchall():
        print(column)

    # Проверка структуры таблицы users
    print("\nСтруктура таблицы users:")
    cursor.execute("PRAGMA table_info(users)")
    for column in cursor.fetchall():
        print(column)

    # Проверка структуры таблицы services
    print("\nСтруктура таблицы services:")
    cursor.execute("PRAGMA table_info(services)")
    for column in cursor.fetchall():
        print(column)

    # Проверка структуры таблицы service_master_price
    print("\nСтруктура таблицы service_master_price:")
    cursor.execute("PRAGMA table_info(service_master_price)")
    for column in cursor.fetchall():
        print(column)

    # Проверка структуры таблицы appointments
    print("\nСтруктура таблицы appointments:")
    cursor.execute("PRAGMA table_info(appointments)")
    for column in cursor.fetchall():
        print(column)

    # Закрываем соединение
    conn.close()

def del_user(user_id):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    # SQL запрос для удаления пользователя по ID
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

def del_service(service_id):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    # SQL запрос для удаления услуги по ID
    cursor.execute("DELETE FROM services WHERE service_id = ?", (service_id,))
    conn.commit()
    conn.close()

def del_master_serv(service_id, master_id):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM service_master_price WHERE service_id = ? AND master_id = ?", (service_id,master_id))
    conn.commit()
    conn.close()

def del_service_master_price(service_master_price_id):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    # SQL запрос для удаления стоимости услуги мастеров по ID
    cursor.execute("DELETE FROM service_master_price WHERE service_master_price_id = ?", (service_master_price_id,))
    conn.commit()
    conn.close()

def del_appointments(appointments_id):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    # SQL запрос для удаления записи по ID
    cursor.execute("DELETE FROM appointments WHERE appointments_id = ?", (appointments_id,))
    conn.commit()
    conn.close()


# Изменение бд под запись
# Функция для получения списка доступных услуг
def get_available_services():
    # Запрашиваем активные записи из таблицы appointments
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    cursor.execute(""" SELECT DISTINCT s.service_id, s.service_name, s.description FROM appointments a JOIN service_master_price sm ON a.service_master_price_id = sm.service_master_price_id JOIN services s ON sm.service_id = s.service_id WHERE a.IsActive = 1 """)
    rows = cursor.fetchall()
    available_services = [{'id': row[0], 'name': row[1], 'description': row[2]} for row in rows]
    return available_services


# Функция для получения полной информации об услуге
def get_service_detail(service_id):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    cursor.execute(
        """ SELECT u.name, smp.price FROM service_master_price smp JOIN users u ON smp.master_id = u.id JOIN services s ON smp.service_id = s.service_id WHERE s.service_id = ? AND smp.service_master_price_id IN ( SELECT service_master_price_id FROM appointments WHERE IsActive = 1 ); """,
        (service_id,)
    )
    rows = cursor.fetchall()
    details = [(name, price) for name, price in rows]
    return details

# Функция для получения полной информации об услуге
def get_service_detail(service_id):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    cursor.execute(
        """ SELECT u.name, smp.price FROM service_master_price smp JOIN users u ON smp.master_id = u.id JOIN services s ON smp.service_id = s.service_id WHERE s.service_id = ? AND smp.service_master_price_id IN ( SELECT service_master_price_id FROM appointments WHERE IsActive = 1 ); """,
        (service_id,)
    )
    rows = cursor.fetchall()
    details = [(name, price) for name, price in rows]
    return details


#Добавляю код для себя
#получение имени услуги по ее id
def get_service_name(service_id):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    cursor.execute("SELECT service_name FROM services WHERE service_id = ?", (service_id,))
    result = cursor.fetchone()
    return result[0] if result else None

#получение service_master_price_id по service_id, name, т.е. по id услуги и имени мастера
def get_service_master_price_id(service_id, name):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    query = """ SELECT smp.service_master_price_id FROM service_master_price smp JOIN users u ON smp.master_id = u.id JOIN services s ON smp.service_id = s.service_id WHERE s.service_id = ? AND u.name = ? """
    cursor.execute(query, (service_id, name))
    result = cursor.fetchone()
    return result[0] if result else None

# #получение уникальных доступных годов
# def get_unique_active_years():
#     conn = sqlite3.connect(DB_NEW)
#     cursor = conn.cursor()
#     cursor.execute(""" SELECT DISTINCT strftime('%Y', appointment_date) AS year FROM appointments WHERE IsActive = 1 """)
#     rows = cursor.fetchall()
#     unique_years = [int(row[0]) for row in rows]
#     return sorted(unique_years)

# получение уникальных доступных годов с учетом service_master_price_id
# def get_unique_active_years(service_master_price_id):
#     conn = sqlite3.connect(DB_NEW)
#     cursor = conn.cursor()
#     cursor.execute(""" SELECT DISTINCT strftime('%Y', appointment_date) AS year FROM appointments WHERE IsActive = 1 AND service_master_price_id = ? """, (service_master_price_id,))
#     rows = cursor.fetchall()
#     unique_years = [int(row[0]) for row in rows]
#     return sorted(unique_years)



# #получение доступных месяцев
# def get_unique_months_in_year(year):
#     conn = sqlite3.connect(DB_NEW)
#     cursor = conn.cursor()
#     cursor.execute(""" SELECT DISTINCT strftime('%m', appointment_date) AS month FROM appointments WHERE IsActive = 1 AND strftime('%Y', appointment_date) = ? """, (str(year),))
#     rows = cursor.fetchall()
#     unique_months = [int(row[0]) for row in rows]
#     return sorted(unique_months)


# получение уникальных доступных месяцев с учетом service_master_price_id
# def get_unique_months_in_year(service_master_price_id, year):
#     conn = sqlite3.connect(DB_NEW)
#     cursor = conn.cursor()
#     cursor.execute(
#         """SELECT DISTINCT strftime('%m', appointment_date) AS month FROM appointments WHERE IsActive = 1 AND strftime('%Y', appointment_date) = ? AND service_master_price_id = ?""",
#         (str(year), service_master_price_id)
#     )
#     rows = cursor.fetchall()
#     unique_months = [int(row[0]) for row in rows]
#     return sorted(unique_months)



# #получение доступных дат
# def get_unique_days_in_month_and_year(service_master_price_id, year, month):
#     conn = sqlite3.connect(DB_NEW)
#     cursor = conn.cursor()
#     cursor.execute(""" SELECT DISTINCT strftime('%d', appointment_date) AS day FROM appointments WHERE IsActive = 1 AND strftime('%Y', appointment_date) = ? AND strftime('%m', appointment_date) = ? """, (str(year), str(month)))
#     rows = cursor.fetchall()
#     unique_days = [int(row[0]) for row in rows]
#     return sorted(unique_days)

# получение уникальных доступных дней с учетом service_master_price_id
# def get_unique_days_in_month_and_year(service_master_price_id, year, month):
#     # Обрабатываем входные параметры, приводя их к строковому виду с ведущими нулями
#     year = f"{year:04}"  # Года всегда передаются в формате YYYY
#     month = f"{int(month):02}"  # Месяцы передаются в формате MM
#     conn = sqlite3.connect(DB_NEW)
#     cursor = conn.cursor()
#     cursor.execute(
#         """SELECT DISTINCT strftime('%d', appointment_date) AS day FROM appointments WHERE IsActive = 1 AND strftime('%Y', appointment_date) = ? AND strftime('%m', appointment_date) = ? AND service_master_price_id = ?""",
#         (year, month, service_master_price_id)
#     )
#     rows = cursor.fetchall()
#     unique_days = [int(row[0]) for row in rows]
#
#     print("Rows:", rows)  # Выводим сырые данные из базы данных
#     print("Unique Days:", unique_days)  # Выводим уникальный отсортированный список дней
#
#     return sorted(unique_days)

#получение доступных временных интервалов для конкретной даты
def get_available_times_for_date(appointment_date):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    cursor.execute(""" SELECT DISTINCT appointment_time FROM appointments WHERE IsActive = 1 AND appointment_date = ? """, (appointment_date,))
    rows = cursor.fetchall()
    available_times = [row[0] for row in rows]
    return available_times

#проверка наличия пользователя в базе данных
def is_user_in_database(user_id):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (user_id,))
    result = cursor.fetchone()
    return bool(result)




# Пример функции для сохранения пользователя-клиента в базу данных
def save_user_to_database(user_id, name, phone_number):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    cursor.execute(''' INSERT INTO users (name, phone_number, role_id, telegram_id) VALUES (?, ?, ?, ?) ''', (name, phone_number, 2, user_id))  # role_id = 2
    conn.commit()
    conn.close()


# Поиск id пользователя по telegram_id
def get_user_id_by_telegram_id(telegram_id):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    query = "SELECT id FROM users WHERE telegram_id = ?"
    cursor.execute(query, (telegram_id,))
    result = cursor.fetchone()

    # Извлекаем первое (и единственное) значение из кортежа
    if result:
        return result[0]
    else:
        return None  # Возвращаем None, если пользователь не найден

# Изменение телеграммовсого id
def update_telegram_id(user_id, new_telegram_id):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE id=?", (user_id,))
    cursor.execute("UPDATE users SET telegram_id=? WHERE id=?", (new_telegram_id, user_id))
    conn.commit()


def get_user_telegram_ids():
    """
    Возвращает список Telegram ID всех пользователей с ролью 'user' (role_id = 2).
    """
    telegram_ids = []
    try:
        # Подключаемся к базе данных
        conn = sqlite3.connect(DB_NEW)
        cursor = conn.cursor()

        # SQL-запрос для получения пользователей с role_id = 2
        cursor.execute("SELECT telegram_id FROM users WHERE role_id = ?", (2,))

        # Получаем все результаты
        rows = cursor.fetchall()

        # Извлекаем только Telegram ID
        telegram_ids = [row[0] for row in rows if row[0] is not None]

    except sqlite3.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")
    finally:
        if conn:
            conn.close()

    return telegram_ids


import sqlite3

#имя мастера, название услуги и стоимость услуги по service_master_price_id
def get_service_info_by_service_master_price_id(service_master_price_id):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    query = """ SELECT u.name, s.service_name, s.price FROM service_master_price AS sm JOIN users AS u ON sm.master_id = u.id JOIN services AS s ON sm.service_id = s.service_id WHERE sm.service_master_price_id = ? """
    cursor.execute(query, (service_master_price_id,))
    result = cursor.fetchone()

    if result is None:
        return "Запись с таким service_master_price_id не найдена."

    name, service_name, price = result
    return {
        'name': name,
        'service_name': service_name,
        'price': price
    }


def get_user_info_by_id(user_id):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    query = "SELECT name, phone_number FROM users WHERE id = ?"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()

    if result is None:
        return "Пользователь с таким ID не найден."

    name, phone_number = result
    return {
        'name': name,
        'phone_number': phone_number
    }


# def get_appointment_id_by_params(appointment_date, appointment_time, service_master_price_id):
#     conn = sqlite3.connect(DB_NEW)
#     cursor = conn.cursor()
#     query = """ SELECT appointments_id FROM appointments WHERE appointment_date = ? AND appointment_time = ? AND service_master_price_id = ? AND IsActive = 1 """
#     cursor.execute(query, (appointment_date, appointment_time, service_master_price_id))
#     result = cursor.fetchone()
#
#     if result is None:
#         return "Назначение не найдено."
#
#     appointments_id = result[0]
#     return appointments_id


# def update_client_id_in_appointment(appointments_id, new_client_id):
#     conn = sqlite3.connect(DB_NEW)
#     cursor = conn.cursor()
#     # Обновляем client_id для указанного назначения
#     cursor.execute("UPDATE appointments SET client_id = ?, IsActive = 0 WHERE appointments_id = ?", (new_client_id, appointments_id))
#     # Сохраняем изменения
#     conn.commit()
#     print("обновлено")



def rename_user_info(telegram_id, name, phone_number):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    # SQL-запрос для обновления записи
    sql = """UPDATE users SET name = ?, phone_number = ? WHERE telegram_id = ?"""
    # Выполнение запроса с параметрами
    cursor.execute(sql, (name, phone_number, telegram_id))
    # Сохранение изменений
    conn.commit()
    conn.close()


def get_user_id_by_telegram_id_show(telegram_id):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    query = "SELECT id FROM users WHERE telegram_id = ?"
    cursor.execute(query, (telegram_id,))
    result = cursor.fetchone()

    if result is None:
        return None

    return result[0]

    conn.close()


# def get_appointments_by_client_id_show(client_id):
#     conn = sqlite3.connect(DB_NEW)
#     cursor = conn.cursor()
#     query = """ SELECT a.appointment_date, a.appointment_time, s.service_name, sm.price, u.name AS client_name, m.name AS master_name FROM appointments a JOIN service_master_price sm ON a.service_master_price_id = sm.service_master_price_id JOIN services s ON sm.service_id = s.service_id JOIN users u ON a.client_id = u.id JOIN users m ON sm.master_id = m.id WHERE a.client_id = ? """
#     cursor.execute(query, (client_id,))
#     results = cursor.fetchall()
#     print(results)
#     return results
#
#     conn.close()



#######################################################################
# Изменение спринта
# Изменение бд под запись
# Функция для получения списка доступных услуг со стоимостью
def get_available_services_new():
    # Запрашиваем активные записи из таблицы appointments
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    cursor.execute(""" SELECT DISTINCT s.service_id, s.service_name, s.description, s.price FROM appointments a JOIN service_master_price sm ON a.master_id = sm.master_id JOIN services s ON sm.service_id = s.service_id WHERE a.IsActive = 1 """)
    rows = cursor.fetchall()
    available_services = [{'id': row[0], 'name': row[1], 'description': row[2], 'price': row[3]} for row in rows]
    return available_services


# Функция для получения полной информации об услуге без стоимости
def get_service_detail_new(service_id):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    cursor.execute(
        """ SELECT DISTINCT u.name FROM service_master_price smp JOIN users u ON smp.master_id = u.id JOIN appointments a ON a.master_id = smp.master_id WHERE a.IsActive = 1 AND smp.service_id = ? """,
        (service_id,)
    )
    rows = cursor.fetchall()
    masters = [name for name, in rows]
    return masters

# получение уникальных доступных годов с учетом service_master_price_id после спринта
def get_unique_active_years_new(service_master_price_id):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    cursor.execute(
        """ SELECT DISTINCT strftime('%Y', a.appointment_date) AS year FROM appointments a JOIN service_master_price smp ON a.master_id = smp.master_id WHERE a.IsActive = 1 AND smp.service_master_price_id = ? """,
        (service_master_price_id,)
    )
    rows = cursor.fetchall()
    unique_years = [int(row[0]) for row in rows]
    return sorted(unique_years)

# получение уникальных доступных месяцев с учетом service_master_price_id после спринта
def get_unique_months_in_year_new(service_master_price_id, year):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    cursor.execute(
        """ SELECT DISTINCT strftime('%m', a.appointment_date) AS month FROM appointments a JOIN service_master_price smp ON a.master_id = smp.master_id WHERE a.IsActive = 1 AND strftime('%Y', a.appointment_date) = ? AND smp.service_master_price_id = ? """,
        (str(year), service_master_price_id)
    )
    rows = cursor.fetchall()
    unique_months = [int(row[0]) for row in rows]
    return sorted(unique_months)

# получение уникальных доступных дней с учетом service_master_price_id
def get_unique_days_in_month_and_year_new(service_master_price_id, year, month):
    # Обрабатываем входные параметры, приводя их к строковому виду с ведущими нулями
    year = f"{year:04}"  # Года всегда передаются в формате YYYY
    month = f"{int(month):02}"  # Месяцы передаются в формате MM
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    cursor.execute(
        """ SELECT DISTINCT strftime('%d', a.appointment_date) AS day FROM appointments a JOIN service_master_price smp ON a.master_id = smp.master_id WHERE a.IsActive = 1 AND strftime('%Y', a.appointment_date) = ? AND strftime('%m', a.appointment_date) = ? AND smp.service_master_price_id = ? """,
        (year, month, service_master_price_id)
    )
    rows = cursor.fetchall()
    unique_days = [int(row[0]) for row in rows]

    print("Rows:", rows)  # Выводим сырые данные из базы данных
    print("Unique Days:", unique_days)  # Выводим уникальный отсортированный список дней

    return sorted(unique_days)


def get_appointment_id_by_params(appointment_date, appointment_time, service_master_price_id):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()

    # Получаем master_id по service_master_price_id
    cursor.execute(
        """ SELECT master_id FROM service_master_price WHERE service_master_price_id = ? """,
        (service_master_price_id,)
    )
    master_id_result = cursor.fetchone()

    if master_id_result is None:
        return "Мастер не найден."

    master_id = master_id_result[0]

    # Находим назначение по master_id, дате и времени
    cursor.execute(
        """ SELECT appointments_id FROM appointments WHERE appointment_date = ? AND appointment_time = ? AND master_id = ? AND IsActive = 1 """,
        (appointment_date, appointment_time, master_id)
    )
    result = cursor.fetchone()

    if result is None:
        return "Назначение не найдено."

    appointments_id = result[0]
    return appointments_id

def update_client_id_in_appointment(appointments_id, new_client_id, new_service_master_price_id):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    # Обновляем client_id и service_master_price_id для указанного назначения
    cursor.execute(
        "UPDATE appointments SET client_id = ?, service_master_price_id = ?, IsActive = 0 WHERE appointments_id = ?",
        (new_client_id, new_service_master_price_id, appointments_id)
    )
    # Сохраняем изменения
    conn.commit()
    print("обновлено")

def get_appointments_by_client_id_show(client_id):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    query = """ SELECT a.appointment_date, a.appointment_time, s.service_name, s.price, u.name AS client_name, m.name AS master_name FROM appointments a JOIN service_master_price sm ON a.service_master_price_id = sm.service_master_price_id JOIN services s ON sm.service_id = s.service_id JOIN users u ON a.client_id = u.id JOIN users m ON sm.master_id = m.id WHERE a.client_id = ? """
    cursor.execute(query, (client_id,))
    results = cursor.fetchall()
    print(results)
    return results

    conn.close()

#

