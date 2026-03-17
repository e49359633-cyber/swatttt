import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import database as db  # Подключаем наш файл БД

# --- КОНФИГ ---
API_TOKEN = '7588624859:AAGlzc_riQhPWg-GnlHSrKmOLEsZ05_-ts8'
ADMINS = ['ramaz666', 'killedfear'] # Ники без @

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def main_menu():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🛒 Каталог", callback_data="catalog"))
    builder.row(types.InlineKeyboardButton(text="👤 Профиль", callback_data="profile"))
    return builder.as_markup()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(f"Привет, {message.from_user.first_name}!", reply_markup=main_menu())

# --- АДМИНКА ---
@dp.message(Command("admin"))
async def admin(message: types.Message):
    if message.from_user.username in ADMINS:
        await message.answer("👑 Меню админа:\n`/add Название Цена`\n`/del ID`")
    else:
        await message.answer("❌ Нет доступа.")

@dp.message(F.text.startswith("/add"))
async def add_item(message: types.Message):
    if message.from_user.username not in ADMINS: return
    try:
        _, name, price = message.text.split()
        db.add_product(name, int(price))
        await message.answer(f"✅ Товар {name} добавлен!")
    except:
        await message.answer("⚠ Ошибка. Пример: `/add VIP 1000`")

@dp.message(F.text.startswith("/del"))
async def del_item(message: types.Message):
    if message.from_user.username not in ADMINS: return
    try:
        _, pid = message.text.split()
        db.delete_product(int(pid))
        await message.answer(f"🗑 Товар с ID {pid} удален.")
    except:
        await message.answer("⚠ Ошибка. Пример: `/del 1`")

# --- КАТАЛОГ ---
@dp.callback_query(F.data == "catalog")
async def catalog(callback: types.CallbackQuery):
    items = db.get_products()
    builder = InlineKeyboardBuilder()
    
    if not items:
        await callback.message.edit_text("Каталог пуст.", reply_markup=main_menu())
        return

    text = "📦 **Список товаров:**\n\n"
    for i in items:
        text += f"🆔 {i[0]} | **{i[1]}** — {i[2]} руб.\n"
        builder.row(types.InlineKeyboardButton(text=f"Купить {i[1]}", callback_data=f"buy_{i[0]}"))
    
    builder.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back"))
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")

@dp.callback_query(F.data == "back")
async def back(callback: types.CallbackQuery):
    await callback.message.edit_text("Главное меню:", reply_markup=main_menu())

async def main():
    db.init_db() # Запускаем БД
    print("Бот в сети!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
