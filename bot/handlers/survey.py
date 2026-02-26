from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
import re

from bot.states.calc import CalcStates, OrderSimilarStates
from bot.keyboards.reply import get_cancel_keyboard, get_contact_keyboard, get_main_keyboard
from bot.database.crud import add_request, get_all_admins_and_managers, add_protected_message, get_car_by_id

router = Router()

# Trigger via Inline button or Reply keyboard
@router.callback_query(F.data == "calc_cost")
async def start_calc_inline(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Пожалуйста, введите ваше ФИО", reply_markup=get_cancel_keyboard())
    await state.set_state(CalcStates.waiting_for_fio)
    await callback.answer()

@router.message(F.text == "Расчет стоимости авто")
async def start_calc_reply(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, введите ваше ФИО", reply_markup=get_cancel_keyboard())
    await state.set_state(CalcStates.waiting_for_fio)

@router.message(CalcStates.waiting_for_fio, F.text)
async def process_fio(message: Message, state: FSMContext):
    # Ensure they didn't click Cancel
    if message.text == "Отменить":
        return
        
    await state.update_data(fio=message.text)
    await message.answer(
        "Введите информацию о желаемом авто (Марка, модель, комплектация, год, бюджет)",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(CalcStates.waiting_for_car_info)

@router.message(CalcStates.waiting_for_car_info, F.text)
async def process_car_info(message: Message, state: FSMContext):
    if message.text == "Отменить":
        return
        
    await state.update_data(car_info=message.text)
    await message.answer(
        "Пожалуйста, предоставьте ваш номер телефона",
        reply_markup=get_contact_keyboard()
    )
    await state.set_state(CalcStates.waiting_for_phone)

@router.message(CalcStates.waiting_for_phone, F.contact | F.text)
async def process_phone(message: Message, state: FSMContext):
    if message.text == "Отменить":
        return
        
    if message.contact:
        phone = message.contact.phone_number
    else:
        phone_text = message.text.strip()
        if not re.match(r"^(?:\+7|7|8)\d{10}$|^9\d{9}$", phone_text):
            await message.answer(
                "Неверный формат, введите номер телефона или нажмите кнопку ниже",
                reply_markup=get_contact_keyboard()
            )
            return
        phone = phone_text

    data = await state.get_data()
    fio = data.get("fio")
    car_info = data.get("car_info")
    # phone is already set above
    
    # Save to database
    await add_request(message.from_user.id, fio, car_info, phone)
    
    # Send confirmation to user
    main_kb = await get_main_keyboard(message.from_user.id)
    await message.answer(
        "СПАСИБО ЗА ОБРАЩЕНИЕ! 😊\nВ ближайшее время мы с вами свяжемся и направим подборку идеального автомобиля в ваш бюджет.",
        reply_markup=main_kb
    )
    
    # Send notification to admins and managers
    admin_users = await get_all_admins_and_managers()
    admin_msg = f"Новая заявка на расчет авто!\n\nФИО: {fio}\nАвто: {car_info}\nТелефон: {phone}\nПользователь: @{message.from_user.username}"
    
    for admin in admin_users:
        try:
            msg = await message.bot.send_message(admin['telegram_id'], admin_msg)
            await add_protected_message(admin['telegram_id'], msg.message_id)
        except Exception:
            pass # ignore if admin blocked the bot
            
    await state.clear()

@router.callback_query(F.data.startswith("order_similar_"))
async def start_order_similar(callback: CallbackQuery, state: FSMContext):
    car_id = int(callback.data.split("_")[2])
    car = await get_car_by_id(car_id)
    if not car:
        await callback.answer("Автомобиль не найден", show_alert=True)
        return
        
    await state.update_data(car_info=f"Из подборки: {car['description']}")
    await callback.message.answer("Решили заказать подобный авто? Отлично!\nПожалуйста, введите ваше ФИО", reply_markup=get_cancel_keyboard())
    await state.set_state(OrderSimilarStates.waiting_for_fio)
    await callback.answer()

@router.message(OrderSimilarStates.waiting_for_fio, F.text)
async def process_similar_fio(message: Message, state: FSMContext):
    if message.text == "Отменить":
        return
        
    await state.update_data(fio=message.text)
    await message.answer(
        "Пожалуйста, предоставьте ваш номер телефона",
        reply_markup=get_contact_keyboard()
    )
    await state.set_state(OrderSimilarStates.waiting_for_phone)

@router.message(OrderSimilarStates.waiting_for_phone, F.contact | F.text)
async def process_similar_phone(message: Message, state: FSMContext):
    if message.text == "Отменить":
        return
        
    if message.contact:
        phone = message.contact.phone_number
    else:
        phone_text = message.text.strip()
        if not re.match(r"^(?:\+7|7|8)\d{10}$|^9\d{9}$", phone_text):
            await message.answer(
                "Неверный формат, введите номер телефона или нажмите кнопку ниже",
                reply_markup=get_contact_keyboard()
            )
            return
        phone = phone_text

    data = await state.get_data()
    fio = data.get("fio")
    car_info = data.get("car_info")
    
    await add_request(message.from_user.id, fio, car_info, phone)
    
    main_kb = await get_main_keyboard(message.from_user.id)
    await message.answer(
        "СПАСИБО ЗА ОБРАЩЕНИЕ! 😊\nВ ближайшее время мы с вами свяжемся и направим подборку идеального автомобиля в ваш бюджет.",
        reply_markup=main_kb
    )
    
    admin_users = await get_all_admins_and_managers()
    admin_msg = f"Новая заявка на подобный авто!\n\nФИО: {fio}\nАвто: {car_info}\nТелефон: {phone}\nПользователь: @{message.from_user.username}"
    
    for admin in admin_users:
        try:
            msg = await message.bot.send_message(admin['telegram_id'], admin_msg)
            await add_protected_message(admin['telegram_id'], msg.message_id)
        except Exception:
            pass
            
    await state.clear()
