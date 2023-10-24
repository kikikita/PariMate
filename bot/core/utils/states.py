from aiogram.fsm.state import StatesGroup, State


class Registration(StatesGroup):
    name = State()
    age = State()
    sex = State()


class Habit(StatesGroup):
    habit_category = State()
    habit_healh = State()
    habit_education = State()
    habit_productivity = State()
    habit_choice = State()
    habit_frequency = State()
    habit_report = State()
