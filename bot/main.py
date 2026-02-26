import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from bot.config import BOT_TOKEN
from bot.database.db import init_db
from bot.handlers import commands, survey, menu, admin

async def main():
    logging.basicConfig(level=logging.INFO)
    
    # Init DB
    await init_db()
    
    # Initialize bot and dp
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher()

    # Register Routers
    dp.include_router(commands.router)
    dp.include_router(survey.router)
    dp.include_router(menu.router)
    dp.include_router(admin.router)

    logging.info("Starting bot...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
