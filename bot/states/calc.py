from aiogram.fsm.state import State, StatesGroup

class CalcStates(StatesGroup):
    waiting_for_fio = State()
    waiting_for_car_info = State()
    waiting_for_phone = State()

class AdminStates(StatesGroup):
    waiting_for_manager_id = State()
    waiting_for_remove_manager_id = State()

class AdminAddCarStates(StatesGroup):
    waiting_for_country = State()
    waiting_for_photos = State()
    waiting_for_description = State()

class OrderSimilarStates(StatesGroup):
    waiting_for_fio = State()
    waiting_for_phone = State()
