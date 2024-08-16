import asyncio
import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime, timedelta

# Подключение к базе данных
conn = sqlite3.connect('birthdays.db')
cursor = conn.cursor()

# Создание таблицы users, если она не существует
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY
)
''')
conn.commit()

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Объект бота
bot = Bot(token="7529165450:AAHoBKyKSYAToSvK6U-Cvpl6l8WlkutA_70")  # Замените на ваш токен
# Диспетчер
dp = Dispatcher()

# Функция для проверки дней рождения
async def check_birthdays():
    today = datetime.today().date()
    tomorrow = today + timedelta(days=1)

    cursor.execute("SELECT name, birthday FROM birthdays")
    birthdays = cursor.fetchall()

    messages = []
    for name, birthday in birthdays:
        birthday_date = datetime.strptime(birthday, "%Y-%m-%d").date()

        if birthday_date == today:
            messages.append(f"Сегодня день рождения у {name}!")
        elif birthday_date == tomorrow:
            messages.append(f"Завтра день рождения у {name}!")

    return messages

# Функция для ежедневной проверки и отправки напоминаний
async def daily_birthday_check():
    while True:
        messages = await check_birthdays()
        if messages:
            # Отправка сообщений всем пользователям, которые запустили бота
            cursor.execute("SELECT user_id FROM users")
            users = cursor.fetchall()
            for user_id in users:
                for message in messages:
                    await bot.send_message(user_id[0], message)
        await asyncio.sleep(86400)  # Ожидание 24 часов

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Добавление пользователя в базу данных
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (message.from_user.id,))
    conn.commit()

    # Проверка на ближайшие дни рождения
    upcoming_birthdays = await check_upcoming_birthdays()

    # Создание кнопки для просмотра ближайших дней рождения
    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Дни рождения в ближайшие 10 дней")],
    ], resize_keyboard=True)

    greeting_message = "Привет! Я бот, который напоминает о днях рождения."
    
    if upcoming_birthdays:
        greeting_message += "\n\nБлижайшие дни рождения:\n" + "\n".join(upcoming_birthdays)
    
    await message.reply(greeting_message, reply_markup=keyboard)

# Функция для проверки дней рождений в ближайшие 10 дней
async def check_upcoming_birthdays():
    today = datetime.today().date()
    ten_days_later = today + timedelta(days=10)

    cursor.execute("SELECT name, birthday FROM birthdays")
    birthdays = cursor.fetchall()

    upcoming_birthdays = []

    for name, birthday in birthdays:
        birthday_date = datetime.strptime(birthday, "%Y-%m-%d").date()
        this_year_birthday = birthday_date.replace(year=today.year)
        
        if today <= this_year_birthday <= ten_days_later:
            upcoming_birthdays.append(f"{name} - {this_year_birthday.strftime('%d %b')}")

    return upcoming_birthdays

# Хэндлер для обработки нажатия на кнопку
@dp.message(lambda message: message.text == "Дни рождения в ближайшие 10 дней")
async def process_upcoming_birthdays(message: types.Message):
    upcoming_birthdays = await check_upcoming_birthdays()

    if upcoming_birthdays:
        await message.reply("Ближайшие дни рождения:\n" + "\n".join(upcoming_birthdays))
    else:
        await message.reply("В ближайшие 10 дней дней рождений нет.")

# Главная функция для запуска бота
async def main():
    # Запуск ежедневной проверки
    asyncio.create_task(daily_birthday_check())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())