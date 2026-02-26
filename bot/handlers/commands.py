import asyncio
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext

from bot.database.crud import add_or_update_user, get_protected_message_ids
from bot.keyboards.reply import get_main_keyboard
from bot.keyboards.inline import get_start_inline_keyboard

router = Router()

import contextlib
from aiogram.exceptions import TelegramBadRequest

async def delete_msg_safe(bot, chat_id, msg_id):
    with contextlib.suppress(Exception):
        await bot.delete_message(chat_id, msg_id)

async def clear_chat(message: Message):
    bot = message.bot
    # Gather message IDs from oldest (N-50) to newest (N) to delete top-down if fallback triggers
    message_ids = list(range(max(0, message.message_id - 50), message.message_id + 1))
    protected_ids = await get_protected_message_ids(message.chat.id, message_ids)
    
    to_delete = [i for i in message_ids if i not in protected_ids]
    
    if not to_delete:
        return
        
    try:
        # Fast bulk deletion
        await bot.delete_messages(chat_id=message.chat.id, message_ids=to_delete)
    except TelegramBadRequest:
        # Fallback gracefully if bulk deletion fails (e.g., messages over 48h)
        tasks = [
            delete_msg_safe(bot, message.chat.id, i)
            for i in to_delete
        ]
        await asyncio.gather(*tasks)

async def start_routine(message: Message, clear: bool = False):
    user = message.from_user
    # Ensure they are in the DB
    await add_or_update_user(user.id, user.full_name, user.username)
    
    greeting = (
        f"Привет, {user.full_name or user.username}! Добро пожаловать.\n\n"
        "🚗 Тануки Авто: Ваш идеальный автомобиль из Азии под ключ! 🚗\n\n"
        "Устали от переплат и неопределенности? Мы привозим автомобили из Японии, Кореи и Китая быстро, честно и с полным сопровождением.\n\n"
        "Почему клиенты выбирают Тануки Авто?\n\n"
        "▪️ Честная цена «под ключ»: Фиксированная комиссия. Никаких сюрпризов и скрытых платежей.\n"
        "▪️ Прозрачность до покупки: Полная история, фотоотчёт и детальная информация о техническом состоянии.\n"
        "▪️ Ваши риски — 0%: Гарантируем 100% возврат предоплаты, если вы передумали.\n"
        "▪️ Скорость и поддержка: Быстрая доставка без задержек и личный менеджер 24/7.\n"
        "▪️ Доставка по всей России: С полным оформлением документов.\n\n"
        "💥 Мечтаете об авто? Не хватает средств?\n"
        "Автокредит без первоначального взноса!\n"
        "Только паспорт и права. Никаких справок и поручителей.\n\n"
        "📍 Где нас найти?\n"
        "Головной офис во Владивостоке:\n"
        "ул. Стрельникова, 7, офис 703\n\n"
        "📞 Оставьте заявку и получите персональный подбор автомобиля вашей мечты! Нажимай кнопку ниже 👇🏼"
    )
    
    keyboard = await get_main_keyboard(user.id)
    inline_kb = get_start_inline_keyboard()
    
    photo = FSInputFile("data/hello.jpeg")
    await message.answer_photo(photo=photo, caption=greeting, reply_markup=inline_kb)
    await message.answer("Выберите действие:", reply_markup=keyboard)

    if clear:
        asyncio.create_task(clear_chat(message))

@router.message(Command("start"))
async def cmd_start(message: Message):
    await start_routine(message, clear=True)

@router.message(Command("clear"))
async def cmd_clear(message: Message):
    await start_routine(message, clear=True)
    
@router.message(F.text == "Отменить")
async def process_cancel(message: Message, state: FSMContext = None):
    if state:
        await state.clear()
    await start_routine(message, clear=True)
