import sqlite3

DB_NAME = 'nailoveBD.sql'

# подключение БД и создание её
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, name varchar(50), pass varchar(50))')
    conn.commit()
    cur.close()
    conn.close()

# Функция добаления пользователя в систему
def add_user(name, password):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("INSERT INTO users (name, pass) VALUES (?, ?)", (name, password))
    conn.commit()
    cur.close()
    conn.close()

# Функция вывода всех пользователей
def get_users():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('SELECT * FROM users')
    users = cur.fetchall()
    cur.close()
    conn.close()
    return users