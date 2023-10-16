from aiogram.fsm.state import StatesGroup, State


class Registration(StatesGroup):
    name = State()
    age = State()
    sex = State()
    category = State()


class Sport(StatesGroup):
    report = State()
    sport_type = State()
    frequency = State()
