from aiogram.fsm.state import StatesGroup, State


class Registration(StatesGroup):
    name = State()
    age = State()
    sex = State()


class Pari(StatesGroup):
    pari_mate_id = State()
    pari_message = State()
    pari_photo_msg = State()
    pari_report = State()
    pari_cancel = State()
    mate_report = State()
    reject_reason = State()


class Habit(StatesGroup):
    habit_category = State()
    habit_choice = State()
    habit_frequency = State()
    habit_cause = State()
    habit_report = State()
    habit_mate_sex = State()
    pari_start = State()
    pari_end = State()
    mate_find = State()
    mate_id = State()
    remove_confirm = State()
