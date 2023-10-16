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
    keyboard_builder.button(text='Спорт')
    keyboard_builder.button(text='Питание')
    keyboard_builder.button(text='Распорядок дня')
    keyboard_builder.adjust(3)

    return keyboard_builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Нажми кнопку, чтобы выбрать категорию'
        )


def sport_type_kb():
    keyboard_builder = ReplyKeyboardBuilder()
    keyboard_builder.button(text='Фитнес')
    keyboard_builder.button(text='Плавание')
    keyboard_builder.button(text='Футбол')
    keyboard_builder.button(text='Волейбол')
    keyboard_builder.button(text='Легкая атлетика')
    keyboard_builder.button(text='Баскетбол')
    keyboard_builder.button(text='Велоспорт')
    keyboard_builder.button(text='Ходьба')
    keyboard_builder.button(text='Теннис')
    keyboard_builder.adjust(3, 3, 3)

    return keyboard_builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Выбери вид спорта, либо укажи свой'
    )
