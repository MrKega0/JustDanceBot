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
        INSERT OR IGNORE INTO users (user_id, username, full_name)
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


# Возвращает 10 последних уроков
async def schedule():
    db = await aiosqlite.connect(DB_NAME)
    lessons_cur = await db.execute("""
        SELECT lesson_id, name, date, time, duration, instructor, capacity, registered_users
        FROM lessons
        ORDER BY date DESC
        LIMIT 10  
        """)
    lessons = await lessons_cur.fetchall()
    await db.close()
    return lessons

async def lesson(lesson_id):
    db = await aiosqlite.connect(DB_NAME)
    lesson_cur = await db.execute(f"""
        SELECT lesson_id, name, date, time, duration, instructor, capacity, registered_users
        FROM lessons
        WHERE lesson_id = {lesson_id}
        """)
    lesson = await lesson_cur.fetchone()
    await db.close()
    return lesson

async def subscriptions(user_id):
    db = await aiosqlite.connect(DB_NAME)
    subscriptions_cur = await db.execute(f"""
        SELECT subscription_id, user_id, remaining_classes, expiration_date
        FROM subscriptions
        WHERE user_id = {user_id}
        """)
    subscriptions = await subscriptions_cur.fetchall()
    await db.close()
    return subscriptions

async def add_subscription(user_id, type, remaining_classes, expiration_date):
    db = await aiosqlite.connect(DB_NAME)
    await db.execute("""
        INSERT INTO subscriptions (user_id, type, remaining_classes, expiration_date)
        VALUES (?, ?, ?, ?)
    """, (user_id, type, remaining_classes, expiration_date))
    await db.commit()
    await db.close()

async def one_day_schedule(date): #Выдаёт расписание на день
    db = await aiosqlite.connect(DB_NAME)
    lessons_cur = await db.execute("""
        SELECT * 
        FROM lessons 
        WHERE date = ? AND capacity - registered_users > 0
        """, (date,))
    lessons = await lessons_cur.fetchall()
    await db.close()
    return lessons

async def create_registration(user_id,lesson_id):
    db = await aiosqlite.connect(DB_NAME)
    # Проверяем, существует ли уже запись
    cursor = await db.execute("SELECT 1 FROM registrations WHERE user_id = ? AND lesson_id = ?", (user_id, lesson_id))
    existing_entry = await cursor.fetchone()

    if existing_entry is not None:
        return 1
    
    cursor = await db.execute("SELECT * FROM subscriptions WHERE user_id = ? AND remaining_classes > 0 AND expiration_date > CURRENT_TIMESTAMP ORDER BY subscription_id")
    existing_entry = cursor.fetchall()

    if existing_entry is not None:
        return 2
    
    # Если записи нет, добавляем новую
    await db.execute("""
        INSERT INTO registrations (user_id, lesson_id, status)
        VALUES (?, ?, ?)
    """, (user_id, lesson_id, 'status'))
    await db.commit()

    await db.execute("""
        UPDATE lessons SET registered_users = registered_users + 1
        WHERE lesson_id = ?
    """, (lesson_id,))

    await db.execute("""
        UPDATE subscriptions SET remaining_classes = remaining_classes - 1
        WHERE subscription_id = ?
    """, (user_id, existing_entry[0][0]))

    await db.commit()
    await db.close()
    return 0

async def main():
    # await add_subscription(1716723260,'test',10,'2025-03-10')
    await add_lesson('Zumba', '2025-02-02', '18:00', 1, 'Ivan',5)

    

if __name__ == '__main__':
    asyncio.run(main())