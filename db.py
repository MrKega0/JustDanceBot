import asyncio
import aiosqlite

# Название файла базы данных
DB_NAME = "schedule_bot.db"

# Функция для создания таблиц
async def create_tables():
    db = await aiosqlite.connect(DB_NAME)
    # Создание таблицы users
    await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            subscription_id INTEGER DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (subscription_id) REFERENCES subscriptions(subscription_id)
        );
    """)
    
    # Создание таблицы subscriptions
    await db.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            subscription_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT,
            remaining_classes INTEGER,
            expiration_date DATE,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
    """)
    
    # Создание таблицы lessons
    await db.execute("""
        CREATE TABLE IF NOT EXISTS lessons (
            lesson_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            date DATE,
            time TIME,
            duration INTEGER,
            instructor TEXT,
            capacity INTEGER,
            registered_users INTEGER DEFAULT 0
        );
    """)
    
    # Создание таблицы registrations
    await db.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            registration_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            lesson_id INTEGER,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (lesson_id) REFERENCES lessons(lesson_id)
        );
    """)
    await db.commit()
    await db.close()
    

# Функция для добавления пользователя
async def add_user(user_id, username, full_name):
    db = await aiosqlite.connect(DB_NAME)
    await db.execute("""
        INSERT INTO users (user_id, username, full_name)
        VALUES (?, ?, ?)
    """, (user_id, username, full_name))
    await db.commit()
    await db.close()

# Функция для добавления абонемента
async def add_subscription(user_id, sub_type, remaining_classes, expiration_date):
    db = await aiosqlite.connect(DB_NAME)
    await db.execute("""
        INSERT INTO subscriptions (user_id, type, remaining_classes, expiration_date)
        VALUES (?, ?, ?, ?)
    """, (user_id, sub_type, remaining_classes, expiration_date))
    await db.commit()
    await db.close()

# Функция для добавления урока
async def add_lesson(name, date, time, duration, instructor, capacity):
    db = await aiosqlite.connect(DB_NAME)
    await db.execute("""
        INSERT INTO lessons (name, date, time, duration, instructor, capacity)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, date, time, duration, instructor, capacity))
    await db.commit()
    await db.close()

# Функция для записи пользователя на урок
async def register_user_for_lesson(user_id, lesson_id, status="Подтверждена"):
    db = await aiosqlite.connect(DB_NAME)
    await db.execute("""
        INSERT INTO registrations (user_id, lesson_id, status)
        VALUES (?, ?, ?)
    """, (user_id, lesson_id, status))
    await db.commit()
    await db.close()

# Возвращает 10 последних уроков
async def shedule():
    db = await aiosqlite.connect(DB_NAME)
    lessons_cur = await db.execute("""
        SELECT name, date, time, duration, instructor, capacity, registered_users
        FROM lessons
        ORDER BY date DESC
        LIMIT 10
        """)
    print(lessons_cur)
    lessons = await lessons_cur.fetchall()
    await db.close()
    return lessons
    
async def main():
    db_shedule = map(str, await shedule())
    text = '\n'.join(db_shedule)
    print(text)

if __name__ == '__main__':
    asyncio.run(main())