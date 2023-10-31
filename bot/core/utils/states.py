from aiogram.fsm.state import StatesGroup, State


class Registration(StatesGroup):
    name = State()
    age = State()
    sex = State()


class Habit(StatesGroup):
    habit_category = State()
    habit_health = State()
    habit_education = State()
    habit_productivity = State()


class Health(StatesGroup):
    habit_choice = State()
    habit_frequency = State()
    habit_cause = State()
    habit_report = State()
    habit_mate_sex = State()
    pari_start = State()
    pari_end = State()


class Education(StatesGroup):
    habit_choice = State()
    habit_frequency = State()
    habit_cause = State()
    habit_report = State()
    habit_mate_sex = State()
    pari_start = State()
    pari_end = State()


class Productivity(StatesGroup):
    habit_choice = State()
    habit_frequency = State()
    habit_cause = State()
    habit_report = State()
    habit_mate_sex = State()
    pari_start = State()
    pari_end = State()
