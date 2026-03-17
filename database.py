import sqlite3

# Путь к файлу базы данных
DB_NAME = 'shop.db'

def init_db():
    """Создает таблицу товаров, если она еще не создана"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_product(name, price):
    """Добавляет новый товар в базу"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO products (name, price) VALUES (?, ?)', (name, price))
    conn.commit()
    conn.close()

def get_products():
    """Возвращает список всех товаров"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    data = cursor.fetchall()
    conn.close()
    return data

def delete_product(prod_id):
    """Удаляет товар по его ID"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM products WHERE id = ?', (prod_id,))
    conn.commit()
    conn.close()
