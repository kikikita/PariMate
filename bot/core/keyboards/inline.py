# from aiogram.types import (
#     ReplyKeyboardMarkup, KeyboardButton, KeyboardButtonPollType
#     )
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_start_kb():
    keyboard_builder = ReplyKeyboardBuilder()
    keyboard_builder.button(text='Найти мотивацию')
    keyboard_builder.button(text='Узнать подробнее о проекте')
    keyboard_builder.adjust(2)

    return keyboard_builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Нажми кнопку,чтобы перейти к выбору цели'
        )


def profile(text: str | list):
    builder = ReplyKeyboardBuilder()

    if isinstance(text, str):
        text = [text]

    [builder.button(text=txt) for txt in text]
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def sex_kb():
    keyboard_builder = ReplyKeyboardBuilder()
    keyboard_builder.button(text='Мужчина')
    keyboard_builder.button(text='Женщина')
    keyboard_builder.adjust(2)

    return keyboard_builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Нажми кнопку, чтобы выбрать пол'
        )


def category_kb():
    keyboard_builder = ReplyKeyboardBuilder()
    keyboard_builder.button(text='Здоровье и спорт')
    keyboard_builder.button(text='Обучение и развитие')
    keyboard_builder.button(text='Личная продуктивность')
    keyboard_builder.adjust(1, 1, 1)

    return keyboard_builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Нажми кнопку, чтобы выбрать категорию'
        )


def healh_kb():
    keyboard_builder = ReplyKeyboardBuilder()
    keyboard_builder.button(text='Заниматься спортом')
    keyboard_builder.button(text='Правильно питаться')
    keyboard_builder.button(text='Пить воду')
    keyboard_builder.button(text='Принимать добавки')
    keyboard_builder.button(text='Делать зарядку')
    keyboard_builder.button(text='Гулять')
    keyboard_builder.button(text='Назад')
    keyboard_builder.adjust(2, 2, 2, 1)
    return keyboard_builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Выбери один из вариантов'
    )


# def sport_type_kb():
#     keyboard_builder = ReplyKeyboardBuilder()
#     keyboard_builder.button(text='Фитнес')
#     keyboard_builder.button(text='Плавание')
#     keyboard_builder.button(text='Футбол')
#     keyboard_builder.button(text='Волейбол')
#     keyboard_builder.button(text='Легкая атлетика')
#     keyboard_builder.button(text='Баскетбол')
#     keyboard_builder.button(text='Велоспорт')
#     keyboard_builder.button(text='Ходьба')
#     keyboard_builder.button(text='Теннис')
#     keyboard_builder.button(text='Назад')
#     keyboard_builder.adjust(3, 3, 3, 1)

#     return keyboard_builder.as_markup(
#         resize_keyboard=True,
#         one_time_keyboard=True,
#         input_field_placeholder='Выбери вид спорта, либо укажи свой'
#     )

def education_kb():
    keyboard_builder = ReplyKeyboardBuilder()
    keyboard_builder.button(text='Изучать новый навык')
    keyboard_builder.button(text='Читать')
    keyboard_builder.button(text='Проходить учебный курс')
    keyboard_builder.button(text='Вести дневник')
    keyboard_builder.button(text='Изучать новый язык')
    keyboard_builder.button(text='Медитировать')
    keyboard_builder.button(text='Назад')

    keyboard_builder.adjust(2, 2, 2, 1)

    return keyboard_builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Выбери один из вариантов'
    )


def productivity_kb():
    keyboard_builder = ReplyKeyboardBuilder()
    keyboard_builder = ReplyKeyboardBuilder()
    keyboard_builder.button(text='Соблюдать режим сна')
    keyboard_builder.button(text='Планировать задачи на день')
    keyboard_builder.button(text='Проводить меньше времени в телефоне')

    keyboard_builder.button(text='Назад')

    keyboard_builder.adjust(2, 1, 1)

    return keyboard_builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Выбери один из вариантов'
    )
