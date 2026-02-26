import aiosqlite
import logging

DB_PATH = 'data/bot_database.sqlite'

async def init_db():
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            # Users table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE NOT NULL,
                    fullname TEXT,
                    username TEXT,
                    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    phone TEXT,
                    role TEXT DEFAULT 'user' -- 'user', 'manager', 'admin'
                )
            ''')
            
            # Requests table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    fio TEXT NOT NULL,
                    car_info TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            ''')
            
            # Protected messages table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS protected_messages (
                    chat_id INTEGER,
                    message_id INTEGER,
                    PRIMARY KEY(chat_id, message_id)
                )
            ''')
            
            # Cars table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS cars (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    country TEXT NOT NULL,
                    description TEXT NOT NULL,
                    photo_ids TEXT NOT NULL
                )
            ''')
            
            await db.commit()
            logging.info("Database initialized successfully.")
    except Exception as e:
        logging.error(f"Failed to initialize database: {e}")
