import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# --- КОНФИГ ---
API_TOKEN = '7588624859:AAGlzc_riQhPWg-GnlHSrKmOLEsZ05_-ts8'
ADMINS = ['ramaz666', 'killedfear'] 
ADMIN_IDS = [8384467554, 8209617821] 
ITEMS_FILE = 'items.txt'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Состояния для ожидания чека
class PaymentStates(StatesGroup):
    waiting_for_receipt = State()

def load_items():
    if not os.path.exists(ITEMS_FILE): return []
    items = []
    with open(ITEMS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip(): items.append(line.strip().split('|'))
    return items

def save_item(name, price, desc):
    with open(ITEMS_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{name}|{price}|{desc}\n")

REQUISITES = (
    "🪙 USDT (TRC20): `UQCHqJyy-SHGrkhdGLjM9GwOE_AJhc2ghdGAu0yorgdeOUUO`\n\n"
    "⚠️ ВАЖНО: Отправьте скриншот чека прямо сюда в чат!"
)

# --- КЛАВИАТУРЫ ---
def main_menu():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🛒 Каталог", callback_data="catalog"))
    builder.row(types.InlineKeyboardButton(text="🤖 Наши боты", callback_data="our_bots"))
    builder.row(types.InlineKeyboardButton(text="👤 Поддержка", url="https://t.me/sapportd"))
    return builder.as_markup()

def bots_menu():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🤖 Root Mail Robot", url="https://t.me/rootmailrobot"))
    builder.row(types.InlineKeyboardButton(text="💣 SMS Bomber Robot", url="https://t.me/smsmsbomrobot"))
    builder.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back"))
    return builder.as_markup()

# --- ХЕНДЛЕРЫ ---
@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(f"Привет, {message.from_user.first_name}!", reply_markup=main_menu())

@dp.callback_query(F.data == "our_bots")
async def show_bots(callback: types.CallbackQuery):
    await callback.message.edit_text("🤖 Наши официальные боты:", reply_markup=bots_menu())

@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.username in ADMINS:
        await message.answer("панель админ\n/add Название Цена Описание")

@dp.message(F.text.startswith("/add"))
async def add_product(message: types.Message):
    if message.from_user.username not in ADMINS: return
    try:
        parts = message.text.split(maxsplit=3)
        save_item(parts[1], parts[2], parts[3])
        await message.answer(f"Добавлен: {parts[1]}")
    except:
        await message.answer("Ошибка. Пример: /add Тест 100 Описание")

@dp.callback_query(F.data == "catalog")
async def show_catalog(callback: types.CallbackQuery):
    items = load_items()
    builder = InlineKeyboardBuilder()
    if not items:
        await callback.message.edit_text("Каталог пуст.", reply_markup=main_menu())
        return
    for idx, item in enumerate(items):
        builder.row(types.InlineKeyboardButton(text=f"{item[0]} — {item[1]}₸", callback_data=f"info_{idx}"))
    builder.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back"))
    await callback.message.edit_text("Выберите товар:", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("info_"))
async def info(callback: types.CallbackQuery):
    idx = int(callback.data.split("_")[1])
    item = load_items()[idx]
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="💳 Купить", callback_data=f"pay_{idx}"))
    builder.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="catalog"))
    await callback.message.edit_text(f"🔹 {item[0]}\n💰 Цена: {item[1]}₸\n\n{item[2]}", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("pay_"))
async def pay(callback: types.CallbackQuery, state: FSMContext):
    idx = int(callback.data.split("_")[1])
    item = load_items()[idx]
    
    await state.update_data(product_name=item[0])
    await state.set_state(PaymentStates.waiting_for_receipt)
    
    await callback.message.edit_text(f"🚀 Оплата {item[0]}\n\n{REQUISITES}")
    await callback.answer()

@dp.message(PaymentStates.waiting_for_receipt, F.photo)
async def handle_receipt(message: types.Message, state: FSMContext):
    data = await state.get_data()
    prod_name = data.get('product_name')
    
    await message.answer("✅ Чек получен! Саппорт проверит оплату.")
    
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_photo(
                admin_id, 
                photo=message.photo[-1].file_id,
                caption=f"💰 НОВЫЙ ЧЕК!\n👤 От: @{message.from_user.username}\n📦 Товар: {prod_name}"
            )
        except: pass
    await state.clear()

@dp.callback_query(F.data == "back")
async def back(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Главное меню:", reply_markup=main_menu())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
