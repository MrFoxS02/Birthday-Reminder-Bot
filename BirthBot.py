import asyncio
import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta

# Подключение к базе данных
conn = sqlite3.connect('birthdays.db')
cursor = conn.cursor()

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Объект бота
bot = Bot(token="7529165450:AAHoBKyKSYAToSvK6U-Cvpl6l8WlkutA_70")  # Замените на ваш токен
# Диспетчер
dp = Dispatcher()

# Функция для проверки дней рождения
async def check_birthdays():
    while True:
        today = datetime.today().date()
        tomorrow = today + timedelta(days=1)

        cursor.execute("SELECT name, birthday FROM birthdays")
        birthdays = cursor.fetchall()

        for name, birthday in birthdays:
            birthday_date = datetime.strptime(birthday, "%Y-%m-%d").date()

            if birthday_date == today:
                await bot.send_message(chat_id='YOUR_CHAT_ID', text=f"Сегодня день рождения у {name}!")
            elif birthday_date == tomorrow:
                await bot.send_message(chat_id='YOUR_CHAT_ID', text=f"Завтра день рождения у {name}!")

        # Задержка до следующей проверки (24 часа)
        await asyncio.sleep(86400)  # 86400 секунд = 24 часа

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Создание кнопки для просмотра ближайших дней рождения
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Ближайшие дни рождения", callback_data="upcoming_birthdays")]
    ])

    await message.reply("Привет! Я бот, который напоминает о днях рождения.", reply_markup=keyboard)

# Хэндлер для обработки нажатия на кнопку
@dp.callback_query(lambda c: c.data == 'upcoming_birthdays')
async def process_upcoming_birthdays(callback_query: types.CallbackQuery):
    today = datetime.today().date()
    ten_days_later = today + timedelta(days=10)

    cursor.execute("SELECT name, birthday FROM birthdays WHERE birthday BETWEEN ? AND ?", (today, ten_days_later))
    birthdays = cursor.fetchall()

    if birthdays:
        upcoming_birthdays = "\n".join([f"{name} - {birthday}" for name, birthday in birthdays])
        await bot.send_message(callback_query.from_user.id, text=f"Ближайшие дни рождения:\n{upcoming_birthdays}")
    else:
        await bot.send_message(callback_query.from_user.id, text="В ближайшие 10 дней дней рождений нет.")

# Функция, которая запускается при старте бота
async def on_startup(dp):
    asyncio.create_task(check_birthdays())

# Главная функция для запуска бота
async def main():
    await on_startup(dp)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
