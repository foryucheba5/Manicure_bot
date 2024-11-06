import sqlite3

DB_NEW = 'nailBD.sql'

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

    # Услуги
    cur.execute(
        ''' CREATE TABLE IF NOT EXISTS services ( 
        service_id INTEGER PRIMARY KEY  AUTOINCREMENT NOT NULL UNIQUE, 
        service_name TEXT NOT NULL, 
        description TEXT NOT NULL ) 
        ''')


    # Стоимость услуги мастеров
    cur.execute(
        ''' CREATE TABLE IF NOT EXISTS service_master_price ( 
        service_master_price_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, 
        service_id INTEGER NOT NULL,
        master_id INTEGER NOT NULL,
        price TEXT NOT NULL,
        FOREIGN KEY (service_id) REFERENCES services (service_id) ON DELETE CASCADE,
        FOREIGN KEY (master_id) REFERENCES users (id) ON DELETE CASCADE
        ) 
        ''')

    # Записи
    cur.execute(
        ''' CREATE TABLE IF NOT EXISTS appointments ( 
        appointments_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
        appointment_date TEXT NOT NULL,
        appointment_time TEXT NOT NULL, 
        service_master_price_id INTEGER NOT NULL,
        appointment_client_id INTEGER,
        IsActive INTEGER NOT NULL CHECK(IsActive IN (0, 1)),
        FOREIGN KEY (service_master_price_id) REFERENCES service_master_price (service_master_price_id) ON DELETE CASCADE,
        FOREIGN KEY (appointment_client_id) REFERENCES users (id) ON DELETE CASCADE
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
def add_master(name, phone, tele_id):
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
    conn.commit()
    conn.close()
    return True

# Добавление услуги
def add_service(service_name, description):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO services (service_name, description) VALUES (?, ?)",
        (service_name, description)
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

def edt_service_price(service_id, master_id, price):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE service_master_price SET price = ? WHERE service_id = ? AND master_id = ?",
        (price, service_id, master_id)
    )
    conn.commit()
    conn.close()


# Добавление стоимости услуги мастеров
def add_service_master_price(service_id, master_id, price):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO service_master_price (service_id, master_id, price) VALUES (?, ?, ?)",
        (service_id, master_id, price)
    )
    conn.commit()
    conn.close()

# Добавление записей
def add_appointments(appointment_date, appointment_time, service_master_price_id, appointment_client_id, IsActive):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO appointments (appointment_date, appointment_time, service_master_price_id, appointment_client_id, IsActive) VALUES (123, 12, 1, 1, 1)"
    )
    conn.commit()
    conn.close()
    a('appointments')

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
    cursor.execute("SELECT s.description, p.price, p.master_id FROM services AS s "
                   "JOIN service_master_price AS p ON s.service_id = p.service_id "
                   "WHERE s.service_id = ?", (serv_id))
    serv = cursor.fetchall()
    conn.close()
    return serv

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