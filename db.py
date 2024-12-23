import sqlite3

# Название файла базы данных
DB_NAME = "schedule_bot.db"

# Функция для создания таблиц
def create_tables():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        # Создание таблицы users
        cursor.execute("""
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
        cursor.execute("""
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
        cursor.execute("""
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
        cursor.execute("""
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
        conn.commit()

# Функция для добавления пользователя
def add_user(user_id, username, full_name):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (user_id, username, full_name)
            VALUES (?, ?, ?)
        """, (user_id, username, full_name))
        conn.commit()

# Функция для добавления абонемента
def add_subscription(user_id, sub_type, remaining_classes, expiration_date):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO subscriptions (user_id, type, remaining_classes, expiration_date)
            VALUES (?, ?, ?, ?)
        """, (user_id, sub_type, remaining_classes, expiration_date))
        conn.commit()

# Функция для добавления урока
def add_lesson(name, date, time, duration, instructor, capacity):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO lessons (name, date, time, duration, instructor, capacity)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, date, time, duration, instructor, capacity))
        conn.commit()

# Функция для записи пользователя на урок
def register_user_for_lesson(user_id, lesson_id, status="Подтверждена"):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO registrations (user_id, lesson_id, status)
            VALUES (?, ?, ?)
        """, (user_id, lesson_id, status))
        conn.commit()

# Возвращает 10 последних уроков
def shedule():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, date, time, duration, instructor, capacity, registered_users
            FROM lessons
            ORDER BY date DESC
            LIMIT 10
        """)
        return cursor.fetchall()
    

db_shedule = map(str,shedule())
text = '\n'.join(db_shedule)
print(text)