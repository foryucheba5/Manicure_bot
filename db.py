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
    #a('users')

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

    # Закрываем соединение
    conn.close()

def del_user(user_id):
    conn = sqlite3.connect(DB_NEW)
    cursor = conn.cursor()
    # SQL запрос для удаления пользователя по ID
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()