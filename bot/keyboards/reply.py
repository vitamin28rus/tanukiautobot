from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from bot.database.crud import get_user_by_tg_id

async def get_main_keyboard(telegram_id: int) -> ReplyKeyboardMarkup:
    """Returns the main reply keyboard. Adds Admin Panel if user is admin or manager."""
    keyboard = [
        [KeyboardButton(text="Расчет стоимости авто")],
        [KeyboardButton(text="Процесс работы"), KeyboardButton(text="Пример договора")],
        [KeyboardButton(text="Информация о компании"), KeyboardButton(text="Процесс оплаты")],
        [KeyboardButton(text="Подборки авто"), KeyboardButton(text="Популярные вопросы")]
    ]

    
    # Check role
    user = await get_user_by_tg_id(telegram_id)
    if user and user['role'] in ('admin', 'manager'):
        keyboard.append([KeyboardButton(text="Панель администратора")])
        
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Returns a simple cancel reply keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Отменить")]],
        resize_keyboard=True
    )

def get_contact_keyboard() -> ReplyKeyboardMarkup:
    """Returns a keyboard to request phone number."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Отправить номер телефона", request_contact=True)],
            [KeyboardButton(text="Отменить")]
        ],
        resize_keyboard=True
    )

def get_finish_photos_keyboard() -> ReplyKeyboardMarkup:
    """Returns a keyboard to finish sending photos."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Завершить отправку фото")],
            [KeyboardButton(text="Отменить")]
        ],
        resize_keyboard=True
    )

def get_faq_reply_keyboard() -> ReplyKeyboardMarkup:
    """Returns a reply keyboard for FAQ questions."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="В моем городе нет офиса компании, как заключить договор?")],
            [KeyboardButton(text="Что означают аббревиатуры ТПО, ЭПТС, СБКТС?")],
            [KeyboardButton(text="Сколько времени занимает доставка автомобиля?")],
            [KeyboardButton(text="Из чего состоит цена авто?")],
            [KeyboardButton(text="Преимущества покупки авто под заказ")],
            [KeyboardButton(text="Назад")]
        ],
        resize_keyboard=True
    )
