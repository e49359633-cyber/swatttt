import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest

# --- КОНФИГ (ОСТАЛСЯ ОДИН) ---
API_TOKEN = '7588624859:AAGlzc_riQhPWg-GnlHSrKmOLEsZ05_-ts8'
ADMINS = ['ramaz666', 'killedfear'] 
ADMIN_IDS = [8384467554, 8209617821] 

ITEMS_FILE = 'items.txt'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- ФУНКЦИИ ФАЙЛА ---
def save_item(name, price, desc):
    with open(ITEMS_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{name}|{price}|{desc}\n")

def load_items():
    if not os.path.exists(ITEMS_FILE):
        return []
    items = []
    with open(ITEMS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                items.append(line.strip().split('|'))
    return items

# --- РЕКВИЗИТЫ ---
REQUISITES = (
    "💳 **Kaspi:** `+7 707 000 00 00`\n"
    "🪙 **USDT (TRC20):** `TАдресКошелька...`\n\n"
    "⚠️ После оплаты пришлите чек: @ramaz666"
)

# --- КЛАВИАТУРЫ ---
def main_menu():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🛒 Каталог товаров", callback_data="catalog"))
    builder.row(types.InlineKeyboardButton(text="👤 Поддержка", url="https://t.me/ramaz666"))
    return builder.as_markup()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(f"Привет, {message.from_user.first_name}!", reply_markup=main_menu())

# --- АДМИНКА ---
@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.username in ADMINS:
        await message.answer(
            "👑 **ПАНЕЛЬ УПРАВЛЕНИЯ**\n\n"
            "Добавить товар:\n"
            "`/add Название Цена Описание`"
        )
    else:
        await message.answer("❌ У вас нет прав админа.")

@dp.message(F.text.startswith("/add"))
async def add_product(message: types.Message):
    if message.from_user.username not in ADMINS:
        return
    try:
        parts = message.text.split(maxsplit=3)
        name, price, desc = parts[1], parts[2], parts[3]
        save_item(name, price, desc)
        await message.answer(f"✅ Товар **{name}** добавлен!")
    except:
        await message.answer("⚠ Ошибка. Пример: `/add VIP_Пак 2500 Описание`")

# --- КАТАЛОГ ---
@dp.callback_query(F.data == "catalog")
async def show_catalog(callback: types.CallbackQuery):
    try:
        items = load_items()
        builder = InlineKeyboardBuilder()
        
        if not items:
            await callback.message.edit_text("Каталог пока пуст.", reply_markup=main_menu())
            await callback.answer()
            return

        text = "📦 **Актуальные предложения:**\n\n"
        for idx, item in enumerate(items):
            text += f"• **{item[0]}** — {item[1]}₸\n"
            builder.row(types.InlineKeyboardButton(text=f"Купить {item[0]}", callback_data=f"info_{idx}"))
        
        builder.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back"))
        await callback.message.edit_text(text, reply_markup=builder.as_markup())
        await callback.answer()
        
    except TelegramBadRequest:
        await callback.answer()

@dp.callback_query(F.data.startswith("info_"))
async def info(callback: types.CallbackQuery):
    idx = int(callback.data.split("_")[1])
    item = load_items()[idx]
    
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="💳 К оплате", callback_data=f"pay_{idx}"))
    builder.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="catalog"))
    
    text = f"🔹 **{item[0]}**\n💰 Цена: {item[1]}₸\n\n📝 {item[2]}"
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()

@dp.callback_query(F.data.startswith("pay_"))
async def pay(callback: types.CallbackQuery):
    idx = int(callback.data.split("_")[1])
    item = load_items()[idx]
    
    await callback.message.edit_text(f"🚀 **Реквизиты для оплаты {item[0]}:**\n\n{REQUISITES}")
    await callback.answer()
    
    for admin_id in ADMIN_IDS:
        if admin_id != 0:
            try:
                await bot.send_message(admin_id, f"🔔 Клиент @{callback.from_user.username} хочет купить: {item[0]}")
            except:
                pass

@dp.callback_query(F.data == "back")
async def back(callback: types.CallbackQuery):
    try:
        await callback.message.edit_text("Главное меню:", reply_markup=main_menu())
    except TelegramBadRequest:
        pass
    await callback.answer()

async def main():
    print("Бот в сети!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
