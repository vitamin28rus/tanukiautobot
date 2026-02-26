from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_start_inline_keyboard() -> InlineKeyboardMarkup:
    """Inline keyboard attached to the welcome message."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Расчитать стоимость авто", callback_data="calc_cost")]
    ])

def get_faq_keyboard() -> InlineKeyboardMarkup:
    """Inline keyboard for FAQ questions."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Доставка автомобиля", callback_data="faq_delivery")],
        [InlineKeyboardButton(text="Что включает в себя стоимость", callback_data="faq_cost")],
        [InlineKeyboardButton(text="Страхуется ли автомобиль", callback_data="faq_insurance")],
        [InlineKeyboardButton(text="Запчасти для китайских авто", callback_data="faq_parts")],
        [InlineKeyboardButton(text="Почему выгодно покупать под заказ", callback_data="faq_profit")],
        [InlineKeyboardButton(text="Как заключить договор (нет офиса)", callback_data="faq_contract")],
        [InlineKeyboardButton(text="Что такое ЭПТС, ТПО, СБКТС", callback_data="faq_terms")],
        [InlineKeyboardButton(text="Сколько времени занимает доставка?", callback_data="faq_time")],
        [InlineKeyboardButton(text="Как осуществляется оплата", callback_data="faq_payment")],
        [InlineKeyboardButton(text="Возвращается ли депозит?", callback_data="faq_deposit")]
    ])

def get_car_picks_keyboard() -> InlineKeyboardMarkup:
    """Inline keyboard for car selections by country."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇯🇵 Япония", callback_data="cars_japan")],
        [InlineKeyboardButton(text="🇰🇷 Корея", callback_data="cars_korea")],
        [InlineKeyboardButton(text="🇨🇳 Китай", callback_data="cars_china")]
    ])

def get_admin_inline_keyboard(is_admin: bool = False) -> InlineKeyboardMarkup:
    """Inline keyboard for the admin panel."""
    buttons = [
        [InlineKeyboardButton(text="Список пользователей", callback_data="admin_users")],
        [InlineKeyboardButton(text="Добавить авто в подборку", callback_data="admin_add_car")],
        [InlineKeyboardButton(text="Назначить менеджера", callback_data="admin_assign_manager")]
    ]
    if is_admin:
        buttons.append([InlineKeyboardButton(text="Удалить менеджера", callback_data="admin_remove_manager")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_admin_add_car_country_keyboard() -> InlineKeyboardMarkup:
    """Inline keyboard for choosing country when adding a car."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇯🇵 Япония", callback_data="add_car_japan")],
        [InlineKeyboardButton(text="🇰🇷 Корея", callback_data="add_car_korea")],
        [InlineKeyboardButton(text="🇨🇳 Китай", callback_data="add_car_china")]
    ])

def get_car_action_keyboard(car_id: int, is_admin: bool = False) -> InlineKeyboardMarkup:
    """Inline keyboard under a car description."""
    buttons = [
        [InlineKeyboardButton(text="Заказать подобный авто", callback_data=f"order_similar_{car_id}")]
    ]
    if is_admin:
        buttons.append([InlineKeyboardButton(text="Удалить авто", callback_data=f"delete_car_{car_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_not_found_car_keyboard() -> InlineKeyboardMarkup:
    """Inline keyboard when no car matches."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Расчитать другое авто", callback_data="calc_cost")]
    ])
