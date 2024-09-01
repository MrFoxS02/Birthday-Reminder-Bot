import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime, timedelta
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

API_TOKEN = ''

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Подключение к базе данных SQLite
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Создание таблицы users, если она не существует
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    full_name TEXT,
    birth_date TEXT,
    family_state TEXT)
''')
conn.commit()


class Form(StatesGroup):
    full_name = State()
    birth_date = State()
    family_state = State()

def save_data(user_id, full_name, birth_date, family_state,):
    cursor.execute('''
    INSERT INTO users (user_id, full_name, birth_date, family_state)
    VALUES (?, ?, ?, ?)
    ''', (user_id, full_name, birth_date, family_state))
    conn.commit()

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    
    # Проверяем, существует ли запись о пользователе
    cursor.execute('SELECT * FROM users_id WHERE user_id = ?', (user_id))
    user = cursor.fetchone()
    
    if not user:
        # Если не существует, добавляем его в БД с пустыми данными
        save_data(user_id, None, None, None, None)
    
    # Создаем объект клавиатуры
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Панель управления")]
        ],
        resize_keyboard=True
    )
    
    # Отправляем сообщение с клавиатурой
    await message.answer("Привет! Я бот-напоминалка о семейных событиях.", reply_markup=keyboard)

@dp.message(lambda message: message.text == "Панель управления")
async def process_panel_control(message: types.Message):
    # Клавиатура с опциями
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [KeyboardButton(text="Добавить новый день рождения")],
            [KeyboardButton(text="Ближайшие дни рождения")]
        ]
    )
    await message.answer("Выберите действие:", reply_markup=keyboard)

async def process_panel_control(message: types.Message):
    # Клавиатура с опциями
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [KeyboardButton(text="Добавить новый день рождения")],
            [KeyboardButton(text="Ближайшие дни рождения")]
        ]
    )
    await message.answer("Выберите действие:", reply_markup=keyboard)

@dp.message(lambda message: message.text == "Добавить новый день рождения")
async def add_birthday(message: types.Message, state: FSMContext):
    await message.answer("Введите полное имя:")
    await state.set_state(Form.full_name)

@dp.message(Form.full_name)
async def process_full_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer("Введите дату рождения в формате ДД.ММ.ГГГГ:")
    await state.set_state(Form.birth_date)

@dp.message(Form.birth_date)
async def process_birth_date(message: types.Message, state: FSMContext):
    try:
        # Проверка корректности ввода даты
        birth_date = datetime.strptime(message.text, "%d.%m.%Y").strftime("%d.%m.%Y")
    except ValueError:
        await message.answer("Пожалуйста, введите корректную дату в формате ДД.ММ.ГГГГ:")
        return
    
    await state.update_data(birth_date=birth_date)
    await message.answer("Кем вам приходится указанный член семьи")
    await state.set_state(Form.family_state)
    
@dp.message(Form.family_state)
async def process_family_state(message: types.Message, state: FSMContext):
    await state.update_data(family_state=message.text)

    
    # Получаем сохраненные данные из состояния
    data = await state.get_data()
    full_name = data.get('full_name')
    birth_date = data.get('birth_date')
    family_state = data.get('family_state')
    user_id = message.from_user.id
    
    # Сохраняем данные пользователя в БД
    save_data(user_id, full_name, birth_date, family_state)
    
    # Отправляем сообщение об успешном добавлении
    await message.answer(f'Данные о дне рождения для {full_name} успешно добавлены.')
    
    # Выводим панель управления
    await process_panel_control(message)
    
    # Сбрасываем состояние
    await state.clear()

@dp.message(lambda message: message.text == "Ближайшие дни рождения")
async def nearest_birthdays(message: types.Message):
    upcoming = []
    days = 30
    user_id = message.from_user.id
    cursor.execute('''
    SELECT full_name, birth_date FROM users
    WHERE user_id = ?
    ORDER BY birth_date ASC
    ''', (user_id,))
    results = cursor.fetchall()

    print(results)

    if results:
        today = datetime.today()
        for name, birth_date in results:
            if birth_date:
                birth_date = datetime.strptime(birth_date, '%d.%m.%Y')

                # Переводим дату рождения на текущий год
                next_birthday = birth_date.replace(year=today.year)

                # Если день рождения уже прошел в этом году, переносим на следующий год
                if next_birthday < today:
                    next_birthday = next_birthday.replace(year=today.year + 1)

                # Добавляем в список, если день рождения в ближайшие 30 дней
                delta = (next_birthday - today).days
                if 0 <= delta <= days:
                    upcoming.append((name, next_birthday))

        # Сортируем по дате
        upcoming.sort(key=lambda x: x[1])

        # Формируем ответное сообщение
        if upcoming:
            response = "Ближайшие дни рождения:\n"
            for name, date in upcoming:
                response += f"{name}: {date.strftime('%d.%m.%Y')}\n"
        else:
            response = "Нет дней рождений в ближайшие 30 дней."
    else:
        response = "Нет сохраненных дней рождений."
    
    await message.answer(response)


async def daily_reminder():
    while True:
        now = datetime.now()
        target_time = now.replace(hour=16, minute=8, second=30, microsecond=0)
        if now > target_time:
            target_time += timedelta(days=1)
        
        await asyncio.sleep((target_time - now).total_seconds())

        today = datetime.today().strftime("%d.%m")

        # Используем substr для извлечения дня и месяца из birth_date
        cursor.execute('''
            SELECT user_id, full_name FROM users
            WHERE substr(birth_date, 1, 5) = ?
        ''', (today,))
        birthdays_today = cursor.fetchall()

        for user_id, full_name in birthdays_today:
            await bot.send_message(user_id, f"Сегодня день рождения у {full_name}!")

async def main():
    asyncio.create_task(daily_reminder())  # Запуск задачи для ежедневной проверки в 08:00
    await dp.start_polling(bot)

if __name__ == '__main__':
    dp.start_polling(bot)

    asyncio.run(main())
