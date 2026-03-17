import asyncio
import sqlite3
import os
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- НАСТРОЙКИ ---
API_TOKEN = '7588624859:AAGlzc_riQhPWg-GnlHSrKmOLEsZ05_-ts8'

ADMINS = ['killedfear', 'ramaz666'] 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- РАБОТА С БАЗОЙ ДАННЫХ ---
def init_db():
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS products 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, price INTEGER)''')
    conn.commit()
    conn.close()

def add_product(name, price):
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO products (name, price) VALUES (?, ?)', (name, price))
    conn.commit()
    conn.close()

def get_products():
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    data = cursor.fetchall()
    conn.close()
    return data

def delete_product(prod_id):
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM products WHERE id = ?', (prod_id,))
    conn.commit()
    conn.close()

# --- КЛАВИАТУРЫ ---
def main_menu():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🛒 Каталог товаров", callback_data="catalog"))
    builder.row(types.InlineKeyboardButton(text="👤 Профиль", callback_data="profile"))
    builder.row(types.InlineKeyboardButton(text="🆘 Поддержка", callback_data="support"))
    return builder.as_markup()

# --- ОБРАБОТЧИКИ ---
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(f"Привет, {message.from_user.first_name}! Это бот-магазин.", reply_markup=main_menu())

@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.username in ADMINS:
        await message.answer(
            "👑 **Админ-панель**\n\n"
            "• `/add Название Цена` — добавить товар\n"
            "• `/del ID` — удалить товар (ID увидишь в каталоге)"
        )
    else:
        await message.answer("❌ У вас нет прав доступа.")

@dp.message(F.text.startswith("/add"))
async def cmd_add(message: types.Message):
    if message.from_user.username not in ADMINS: return
    try:
        _, name, price = message.text.split()
        add_product(name, int(price))
        await message.answer(f"✅ Товар '{name}' успешно добавлен!")
    except:
        await message.answer("⚠ Ошибка! Пиши так: `/add Пакет1 1000` (без пробелов в названии)")

@dp.message(F.text.startswith("/del"))
async def cmd_del(message: types.Message):
    if message.from_user.username not in ADMINS: return
    try:
        _, prod_id = message.text.split()
        delete_product(int(prod_id))
        await message.answer(f"🗑 Товар с ID {prod_id} удален.")
    except:
        await message.answer("⚠ Ошибка! Пиши так: `/del 1` (где 1 — это ID товара)")

@dp.callback_query(F.data == "catalog")
async def show_catalog(callback: types.CallbackQuery):
    products = get_products()
    builder = InlineKeyboardBuilder()
    
    if not products:
        await callback.message.edit_text("Каталог пока пуст.", reply_markup=main_menu())
        return

    text = "📦 **Наши товары:**\n\n"
    for p in products:
        # p[0] - ID, p[1] - Name, p[2] - Price
        text += f"🆔 {p[0]} | **{p[1]}** — {p[2]} руб.\n"
        builder.row(types.InlineKeyboardButton(text=f"Купить {p[1]}", callback_data=f"buy_{p[0]}"))
    
    builder.row(types.InlineKeyboardButton(text="⬅️ В меню", callback_data="back"))
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")

@dp.callback_query(F.data == "back")
async def back(callback: types.CallbackQuery):
    await callback.message.edit_text("Главное меню магазина:", reply_markup=main_menu())

async def main():
    init_db() # Создаем базу при запуске
    print("Бот успешно запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
