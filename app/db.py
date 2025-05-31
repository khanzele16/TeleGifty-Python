import sqlite3
import logging
import json
from datetime import datetime
from aiogram.types import Message

def register_user(message: Message):
    conn = sqlite3.connect('telegift.sql')
    cur = conn.cursor()
    # Создание таблиц SQL
    # Создание таблицы Users
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            name TEXT
        )
    ''')
    # Создание таблицы History
    cur.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            gift_id TEXT,
            value INTEGER,
            purchased_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    # Создание таблицы Cart
    cur.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            gift_id TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    # Регистрация пользователя
    cur.execute('INSERT OR IGNORE INTO users (id, username, name) VALUES (?, ?, ?)',
        (message.from_user.id, message.from_user.username, message.from_user.first_name)
    )
    conn.commit()
    cur.close()
    conn.close()

def get_history(message: Message):
    conn = sqlite3.connect('telegift.sql')
    cur = conn.cursor()
    cur.execute('SELECT gift_id, value, purchased_at FROM history WHERE user_id = ?', (message.from_user.id,))
    rows = cur.fetchall()
    history = []
    for gift_json, value, date in rows:
        try:
            gift_ids = json.loads(gift_json)
        except json.JSONDecodeError:
            gift_ids = []
        history.append((gift_ids, value, date))
    cur.close()
    conn.close()
    return history

def add_to_history(user_id: int, gift_ids: list[str], value: int):
    conn = sqlite3.connect('telegift.sql')
    cur = conn.cursor()
    gift_ids_json = json.dumps(gift_ids)
    timestamp = datetime.now().isoformat()
    cur.execute(
        'INSERT INTO history (user_id, gift_id, value, purchased_at) VALUES (?, ?, ?, ?)',
        (user_id, gift_ids_json, value, timestamp)
    )
    conn.commit()
    cur.close()
    conn.close()

def get_cart(user_id: int):
    conn = sqlite3.connect('telegift.sql')
    cur = conn.cursor()
    cur.execute('SELECT gift_id FROM cart WHERE user_id = ?', (user_id,))
    rows = cur.fetchall()
    cart = [row[0] for row in rows]
    print(cart)
    cur.close()
    conn.close()
    return cart

def add_to_cart(user_id: int, gift_id: str):
    conn = sqlite3.connect('telegift.sql')
    cur = conn.cursor()
    cur.execute('INSERT INTO cart (user_id, gift_id) VALUES (?, ?)', (user_id, gift_id))
    conn.commit()
    logging.info(f"Подарок {gift_id} добавлен в корзину пользователя {user_id}")
    cur.execute("PRAGMA table_info(cart)")
    columns = cur.fetchall()
    logging.info(f"Структура таблицы cart: {columns}")
    cur.close()
    conn.close()

def clean_cart(user_id: int):
    conn = sqlite3.connect('telegift.sql')
    cur = conn.cursor()
    cur.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))
    conn.commit()
    cur.close()
    conn.close()