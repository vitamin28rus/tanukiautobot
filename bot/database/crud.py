import aiosqlite
import json
from bot.database.db import DB_PATH
from bot.config import ADMIN_IDS

async def add_or_update_user(telegram_id: int, fullname: str, username: str):
    async with aiosqlite.connect(DB_PATH) as db:
        if telegram_id in ADMIN_IDS:
            await db.execute('''
                INSERT INTO users (telegram_id, fullname, username, role)
                VALUES (?, ?, ?, 'admin')
                ON CONFLICT(telegram_id) DO UPDATE SET
                fullname=excluded.fullname,
                username=excluded.username,
                role='admin';
            ''', (telegram_id, fullname, username))
        else:
            await db.execute('''
                INSERT INTO users (telegram_id, fullname, username, role)
                VALUES (?, ?, ?, 'user')
                ON CONFLICT(telegram_id) DO UPDATE SET
                fullname=excluded.fullname,
                username=excluded.username;
            ''', (telegram_id, fullname, username))
        await db.commit()

async def get_user_by_tg_id(telegram_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,)) as cursor:
            return await cursor.fetchone()

async def add_request(telegram_id: int, fio: str, car_info: str, phone: str):
    user = await get_user_by_tg_id(telegram_id)
    if not user:
        return None
        
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO requests (user_id, fio, car_info, phone)
            VALUES (?, ?, ?, ?)
        ''', (user['id'], fio, car_info, phone))
        
        # update user's phone if we just got it
        await db.execute('''
            UPDATE users SET phone = ? WHERE id = ?
        ''', (phone, user['id']))
        await db.commit()

async def get_all_users():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM users ORDER BY join_date DESC') as cursor:
            return await cursor.fetchall()

async def get_all_admins_and_managers():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE role IN ('admin', 'manager')") as cursor:
            return await cursor.fetchall()

async def get_all_managers():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE role = 'manager'") as cursor:
            return await cursor.fetchall()
            
async def assign_manager(target_identifier: str) -> bool:
    """
    Target identifier can be integer (telegram_id) or string (username without @).
    Updates user role to 'manager'. Returns True if successful.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            target_id = int(target_identifier)
            query = "UPDATE users SET role = 'manager' WHERE telegram_id = ?"
            params = (target_id,)
        except ValueError:
            target_username = target_identifier.replace('@', '')
            query = "UPDATE users SET role = 'manager' WHERE username = ?"
            params = (target_username,)
            
        cursor = await db.execute(query, params)
        await db.commit()
        return cursor.rowcount > 0

async def remove_manager(target_identifier: str) -> bool:
    """
    Target identifier can be integer (telegram_id) or string (username without @).
    Updates user role to 'user' if they were 'manager'. Returns True if successful.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            target_id = int(target_identifier)
            query = "UPDATE users SET role = 'user' WHERE telegram_id = ? AND role = 'manager'"
            params = (target_id,)
        except ValueError:
            target_username = target_identifier.replace('@', '')
            query = "UPDATE users SET role = 'user' WHERE username = ? AND role = 'manager'"
            params = (target_username,)
            
        cursor = await db.execute(query, params)
        await db.commit()
        return cursor.rowcount > 0

async def add_protected_message(chat_id: int, message_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT OR IGNORE INTO protected_messages (chat_id, message_id)
            VALUES (?, ?)
        ''', (chat_id, message_id))
        await db.commit()

async def get_protected_message_ids(chat_id: int, message_ids: list[int]) -> set[int]:
    if not message_ids:
        return set()
    async with aiosqlite.connect(DB_PATH) as db:
        placeholders = ','.join(['?'] * len(message_ids))
        query = f'SELECT message_id FROM protected_messages WHERE chat_id = ? AND message_id IN ({placeholders})'
        async with db.execute(query, (chat_id, *message_ids)) as cursor:
            rows = await cursor.fetchall()
            return {row[0] for row in rows}

async def add_car(country: str, description: str, photo_ids: list[str]) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        photo_ids_json = json.dumps(photo_ids)
        cursor = await db.execute('''
            INSERT INTO cars (country, description, photo_ids)
            VALUES (?, ?, ?)
        ''', (country, description, photo_ids_json))
        car_id = cursor.lastrowid
        await db.commit()
        return car_id

async def get_cars_by_country(country: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM cars WHERE country = ? ORDER BY id DESC', (country,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def get_car_by_id(car_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM cars WHERE id = ?', (car_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def delete_car(car_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('DELETE FROM cars WHERE id = ?', (car_id,))
        await db.commit()
        return cursor.rowcount > 0
