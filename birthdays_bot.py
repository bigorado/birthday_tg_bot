import sqlite3
import asyncio
import logging
import pytz
from aiogram import Bot, Dispatcher, types, Router, BaseMiddleware
from aiogram.types import Message, TelegramObject
from aiogram.filters import Command
from datetime import datetime, timedelta
from random import choice
from apscheduler.schedulers.asyncio import AsyncIOScheduler

TOKEN = "<BOT_TOKEN>" # Заменить на ваш токен бота
GROUP_CHAT_ID = <YOUR_CHAT_ID>  # Замените на ваш ID группы
ADMIN_ID = <YOUR_TG_ID>  # Замените на ваш user_id

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()

# Инициализация планировщика
scheduler = AsyncIOScheduler(timezone=pytz.timezone("Europe/Moscow"))

# Middleware для проверки прав доступа
class AccessMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data):
        if isinstance(event, Message):  # Проверяем, что это сообщение
            if event.from_user.id != ADMIN_ID:  # Проверка на админа
                await event.answer("❌ У вас нет доступа к командам.")
                return
        return await handler(event, data)

# Подключаем middleware к роутеру
router.message.middleware(AccessMiddleware())

# Инициализация базы данных
def init_db():
    try:
        conn = sqlite3.connect("birthdays.db")
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS birthdays (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            username TEXT NOT NULL,
                            birthday DATE NOT NULL,
                            donation_link TEXT NOT NULL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS greetings (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            text TEXT NOT NULL)''')
        conn.commit()
        conn.close()
        logging.info("✅ База данных инициализирована")
    except Exception as e:
        logging.error(f"🚨 Ошибка при инициализации базы данных: {e}")

# Функция для добавления дня рождения в базу данных
async def add_birthday(name: str, username: str, birthday: str, donation_link: str):
    conn = sqlite3.connect("birthdays.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO birthdays (name, username, birthday, donation_link) VALUES (?, ?, ?, ?)",
                   (name, username, birthday, donation_link))
    conn.commit()
    conn.close()

# Случайный выбор поздравления
def get_random_greeting():
    conn = sqlite3.connect("birthdays.db")
    cursor = conn.cursor()
    cursor.execute("SELECT text FROM greetings ORDER BY RANDOM() LIMIT 1")
    greeting = cursor.fetchone()
    conn.close()
    return greeting[0] if greeting else "🎉 Поздравляем!"

# Проверка дней рождения
async def check_birthdays():
    logging.info("🔄 Запуск проверки дней рождения")
    today = datetime.now().strftime("%m-%d")  # Только месяц и день
    logging.info(f"🔎 Проверяем ДР на {today}")

    conn = sqlite3.connect("birthdays.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, username, donation_link FROM birthdays WHERE strftime('%m-%d', birthday) = ?", (today,))
    birthdays = cursor.fetchall()
    conn.close()

    if not birthdays:
        logging.info("❌ Сегодня нет именинников.")
    else:
        for name, username, donation_link in birthdays:
            greeting = get_random_greeting()
            text = f"🎉 Сегодня день рождения у {name} {username}! 🎂\n\n{greeting}\n\nСбор на подарок тут: {donation_link}"
            try:
                logging.info(f"🔄 Пытаюсь отправить сообщение для {name} в группу {GROUP_CHAT_ID}")
                await bot.send_message(GROUP_CHAT_ID, text)
                logging.info(f"✅ Сообщение отправлено для {name}")
            except Exception as e:
                logging.error(f"🚨 Ошибка отправки сообщения: {e}")

# Уведомление за неделю до дня рождения
async def check_upcoming_birthdays():
    logging.info("🔄 Запуск проверки предстоящих дней рождения")
    today = datetime.now()
    next_week = (today + timedelta(days=7)).strftime("%m-%d")  # Только месяц и день
    logging.info(f"🔎 Проверяем ДР на следующую неделю ({next_week})")

    conn = sqlite3.connect("birthdays.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, username, birthday FROM birthdays WHERE strftime('%m-%d', birthday) = ?", (next_week,))
    upcoming_birthdays = cursor.fetchall()
    conn.close()

    if not upcoming_birthdays:
        logging.info("❌ На следующую неделю нет именинников.")
    else:
        for name, username, birthday in upcoming_birthdays:
            text = f"🎉 Через неделю {birthday} день рождения у {name} {username}!"
            try:
                logging.info(f"🔄 Пытаюсь отправить уведомление для {name} в личный чат {ADMIN_ID}")
                await bot.send_message(ADMIN_ID, text)
                logging.info(f"✅ Уведомление отправлено для {name}")
            except Exception as e:
                logging.error(f"🚨 Ошибка отправки уведомления: {e}")

# Обработчик команды /add
@router.message(Command("add"))
async def add_command(message: Message):
    args = message.text.split(maxsplit=4)
    if len(args) < 5:
        await message.reply("Использование: /add Имя @username ДД.ММ.ГГГГ ссылка_на_донат")
        return

    name, username, birthday, donation_link = args[1], args[2], args[3], args[4]
    try:
        birthday = datetime.strptime(birthday, "%d.%m.%Y").strftime("%Y-%m-%d")
        await add_birthday(name, username, birthday, donation_link)
        await message.reply("✅ ДР добавлен!")
    except ValueError:
        await message.reply("❌ Ошибка в формате даты! Используйте ДД.ММ.ГГГГ")

# Обработчик команды /delete_user
@router.message(Command("delete_user"))
async def delete_user_command(message: Message):
    if message.from_user.id != ADMIN_ID:  # Проверка на админа
        await message.reply("❌ У вас нет доступа к этой команде.")
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("Использование: /delete_user @username")
        return

    username = args[1]
    conn = sqlite3.connect("birthdays.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM birthdays WHERE username = ?", (username,))
    conn.commit()
    conn.close()

    await message.reply(f"✅ Пользователь @{username} удалён из базы данных!")

# Обработчик команды /update_link
@router.message(Command("update_link"))
async def update_link_command(message: Message):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.reply("Использование: /update_link @username новая_ссылка")
        return

    username, new_link = args[1], args[2]
    conn = sqlite3.connect("birthdays.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE birthdays SET donation_link = ? WHERE username = ?", (new_link, username))
    conn.commit()
    conn.close()

    await message.reply(f"✅ Ссылка для {username} обновлена!")

# Обработчик команды /update_name
@router.message(Command("update_name"))
async def update_name_command(message: Message):
    if message.from_user.id != ADMIN_ID:  # Проверка на админа
        await message.reply("❌ У вас нет доступа к этой команде.")
        return

    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.reply("Использование: /update_name @username новое_имя")
        return

    username, new_name = args[1], args[2]
    conn = sqlite3.connect("birthdays.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE birthdays SET name = ? WHERE username = ?", (new_name, username))
    conn.commit()
    conn.close()

    await message.reply(f"✅ Имя для {username} обновлено на {new_name}!")

# Обработчик команды /add_greeting
@router.message(Command("add_greeting"))
async def add_greeting_command(message: Message):
    greeting_text = message.text.split(maxsplit=1)[1]
    conn = sqlite3.connect("birthdays.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO greetings (text) VALUES (?)", (greeting_text,))
    conn.commit()
    conn.close()

    await message.reply("✅ Поздравление добавлено!")

# Обработчик команды /list
@router.message(Command("list"))
async def list_command(message: Message):
    if message.from_user.id != ADMIN_ID:  # Проверка на админа
        await message.reply("❌ У вас нет доступа к этой команде.")
        return

    conn = sqlite3.connect("birthdays.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, username, birthday FROM birthdays")
    users = cursor.fetchall()
    conn.close()

    if not users:
        await message.reply("❌ В базе данных нет записей.")
        return

    response = "📜 Список всех пользователей и их дней рождений:\n\n"
    for name, username, birthday in users:
        response += f"👤 {name} -  {username} - {birthday}\n"

    await message.reply(response)

# Обработчик команды /help
@router.message(Command("help"))
async def help_command(message: Message):
    help_text = """
📜 Список команд:

/add - Добавить день рождения
Использование: /add Имя @username ДД.ММ.ГГГГ ссылка_на_донат
Пример: /add Ивана @username 16.03.1991 https://example.com

/update_link - Обновить ссылку на донат
Использование: /update_link @username новая_ссылка
Пример: /update_link @username https://newlink.com

/update_name - Обновить имя
Использование: /update_name @username новое_имя
Пример: /update_name @username Ивана

/delete_user - Удалить пользователя
Использование: /delete_user @username
Пример: /delete_user @username

/add_greeting - Добавить поздравление
Использование: /add_greeting текст_поздравления
Пример: /add_greeting С днём рождения, бро! 🎉

/list - Показать список всех пользователей и их дней рождений
    """
    await message.reply(help_text)

# Подключаем роутер к диспетчеру
dp.include_router(router)

# Запуск бота и задач
async def main():
    init_db()
    logging.info("🔄 Бот запущен")

    # Настройка планировщика
    scheduler.add_job(check_birthdays, "cron", hour=9, minute=0, timezone="Europe/Moscow")
    logging.info("✅ Задача check_birthdays добавлена в планировщик")
    scheduler.add_job(check_upcoming_birthdays, "cron", hour=9, minute=0, timezone="Europe/Moscow")
    logging.info("✅ Задача check_upcoming_birthdays добавлена в планировщик")

    # Тестовая задача (запуск через 10 секунд)
#    scheduler.add_job(check_birthdays, "date", run_date=datetime.now() + timedelta(seconds=10))
#    logging.info("✅ Тестовая задача добавлена (запуск через 10 секунд)")

    # Запуск планировщика
    scheduler.start()
    logging.info("🔄 Планировщик запущен")

    # Запуск бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    logging.getLogger('apscheduler').setLevel(logging.DEBUG)
    asyncio.run(main())
