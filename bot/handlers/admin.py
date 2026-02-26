from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.fsm.context import FSMContext

from bot.database.crud import get_all_users, assign_manager, get_user_by_tg_id, add_car, delete_car, get_all_managers, remove_manager
from bot.keyboards.inline import get_admin_inline_keyboard, get_admin_add_car_country_keyboard
from bot.keyboards.reply import get_cancel_keyboard, get_main_keyboard, get_finish_photos_keyboard
from bot.states.calc import AdminStates, AdminAddCarStates

router = Router()

async def ensure_admin_or_manager(telegram_id: int):
    user = await get_user_by_tg_id(telegram_id)
    if user and user['role'] in ('admin', 'manager'):
        return True
    return False

@router.message(F.text == "Панель администратора")
async def admin_panel(message: Message):
    user = await get_user_by_tg_id(message.from_user.id)
    if not user or user['role'] not in ('admin', 'manager'):
        await message.answer("У вас нет доступа к этой команде.")
        return
        
    is_admin = user['role'] == 'admin'
    await message.answer("Панель администратора. Выберите действие:", reply_markup=get_admin_inline_keyboard(is_admin))

@router.callback_query(F.data == "admin_users")
async def admin_list_users(callback: CallbackQuery):
    if not await ensure_admin_or_manager(callback.from_user.id):
        return
        
    users = await get_all_users()
    if not users:
        await callback.message.answer("Список пользователей пуст.")
        return
        
    msg = "Список пользователей:\n\n"
    for idx, u in enumerate(users[:50]): # Limit to latest 50 for telegram message size limits
        phone = u['phone'] if u['phone'] else 'Нет'
        username = f"@{u['username']}" if u['username'] else "Нет"
        msg += f"{idx+1}. Имя: {u['fullname']} | Ник: {username} | Тел: {phone} | Дата: {u['join_date'][:10]} | Роль: {u['role']}\n"
    
    await callback.message.answer(msg)
    await callback.answer()

@router.callback_query(F.data == "admin_assign_manager")
async def start_assign_manager(callback: CallbackQuery, state: FSMContext):
    if not await ensure_admin_or_manager(callback.from_user.id):
        return
        
    await callback.message.answer("Введите Telegram ID или Username (без @) пользователя которого хотите назначить менеджером:", reply_markup=get_cancel_keyboard())
    await state.set_state(AdminStates.waiting_for_manager_id)
    await callback.answer()

@router.message(AdminStates.waiting_for_manager_id, F.text)
async def process_assign_manager(message: Message, state: FSMContext):
    if message.text == "Отменить":
        await state.clear()
        return

    success = await assign_manager(message.text.strip())
    main_kb = await get_main_keyboard(message.from_user.id)
    
    if success:
        await message.answer(f"Пользователь {message.text} успешно назначен менеджером!", reply_markup=main_kb)
    else:
        await message.answer(f"Не удалось найти пользователя с идентификатором {message.text}.", reply_markup=main_kb)
        
    await state.clear()

@router.callback_query(F.data == "admin_remove_manager")
async def start_remove_manager(callback: CallbackQuery, state: FSMContext):
    user = await get_user_by_tg_id(callback.from_user.id)
    if not user or user['role'] != 'admin':
        await callback.answer("У вас нет доступа к этой команде.", show_alert=True)
        return
        
    managers = await get_all_managers()
    if not managers:
        await callback.message.answer("Список менеджеров пуст.")
        await callback.answer()
        return
        
    msg = "Список менеджеров:\n\n"
    for idx, u in enumerate(managers):
        phone = u['phone'] if u['phone'] else 'Нет'
        username = f"@{u['username']}" if u['username'] else "Нет"
        msg += f"{idx+1}. Имя: {u['fullname']} | Ник: {username} | Тел: {phone} | ID: {u['telegram_id']}\n"
    
    msg += "\nВведите Telegram ID или Username (без @) менеджера которого хотите удалить:"
        
    await callback.message.answer(msg, reply_markup=get_cancel_keyboard())
    await state.set_state(AdminStates.waiting_for_remove_manager_id)
    await callback.answer()

@router.message(AdminStates.waiting_for_remove_manager_id, F.text)
async def process_remove_manager(message: Message, state: FSMContext):
    if message.text == "Отменить":
        await state.clear()
        main_kb = await get_main_keyboard(message.from_user.id)
        await message.answer("Действие отменено.", reply_markup=main_kb)
        return

    success = await remove_manager(message.text.strip())
    main_kb = await get_main_keyboard(message.from_user.id)
    
    if success:
        await message.answer(f"Пользователь {message.text} успешно удален из менеджеров!", reply_markup=main_kb)
    else:
        await message.answer(f"Не удалось найти менеджера с идентификатором {message.text}.", reply_markup=main_kb)
        
    await state.clear()

@router.callback_query(F.data == "admin_add_car")
async def admin_add_car(callback: CallbackQuery, state: FSMContext):
    if not await ensure_admin_or_manager(callback.from_user.id):
        return
        
    await callback.message.answer("Выберите страну для подборки:", reply_markup=get_admin_add_car_country_keyboard())
    await state.set_state(AdminAddCarStates.waiting_for_country)
    await callback.answer()

@router.callback_query(AdminAddCarStates.waiting_for_country, F.data.startswith("add_car_"))
async def process_add_car_country(callback: CallbackQuery, state: FSMContext):
    country_map = {
        "add_car_japan": "japan",
        "add_car_korea": "korea",
        "add_car_china": "china"
    }
    country = country_map.get(callback.data)
    if not country:
        return

    await state.update_data(country=country, photos=[])
    await callback.message.answer(
        "Теперь отправьте фотографии автомобиля (по одной или альбомом). После отправки всех фото нажмите «Завершить отправку фото».",
        reply_markup=get_finish_photos_keyboard()
    )
    await state.set_state(AdminAddCarStates.waiting_for_photos)
    await callback.answer()

@router.message(AdminAddCarStates.waiting_for_photos, F.photo)
async def process_add_car_photos(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    
    file_id = message.photo[-1].file_id
    photos.append(file_id)
    
    await state.update_data(photos=photos)
    
@router.message(AdminAddCarStates.waiting_for_photos, F.text == "Завершить отправку фото")
async def process_finish_photos(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    
    if not photos:
        await message.answer("Вы не отправили ни одной фотографии! Отправьте фото или нажмите «Отменить».")
        return
        
    await message.answer("Фотографии получены. Теперь отправьте описание автомобиля:", reply_markup=get_cancel_keyboard())
    await state.set_state(AdminAddCarStates.waiting_for_description)

@router.message(AdminAddCarStates.waiting_for_photos, F.text == "Отменить")
@router.message(AdminAddCarStates.waiting_for_description, F.text == "Отменить")
async def process_cancel_add_car(message: Message, state: FSMContext):
    await state.clear()
    main_kb = await get_main_keyboard(message.from_user.id)
    await message.answer("Добавление автомобиля отменено.", reply_markup=main_kb)

@router.message(AdminAddCarStates.waiting_for_description, F.text)
async def process_add_car_description(message: Message, state: FSMContext):
    if message.text == "Отменить":
        await process_cancel_add_car(message, state)
        return

    data = await state.get_data()
    country = data.get("country")
    photos = data.get("photos")
    description = message.text
    
    await add_car(country, description, photos)
    
    await state.clear()
    main_kb = await get_main_keyboard(message.from_user.id)
    await message.answer("Автомобиль успешно добавлен в подборку!", reply_markup=main_kb)

@router.callback_query(F.data.startswith("delete_car_"))
async def process_delete_car(callback: CallbackQuery):
    if not await ensure_admin_or_manager(callback.from_user.id):
        await callback.answer("У вас нет прав для этого действия", show_alert=True)
        return
        
    try:
        car_id = int(callback.data.split("_")[2])
        success = await delete_car(car_id)
        
        if success:
            await callback.message.answer("Автомобиль успешно удален.")
        else:
            await callback.message.answer("Автомобиль не найден или уже был удален.")
    except Exception as e:
        await callback.message.answer("Во время удаления произошла ошибка.")
        
    await callback.answer()
