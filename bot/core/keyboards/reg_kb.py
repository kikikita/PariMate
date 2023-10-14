# from aiogram.types import (
#     ReplyKeyboardMarkup, KeyboardButton, KeyboardButtonPollType
#     )
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_reply_keyboard():
    keyboard_builder = ReplyKeyboardBuilder()
    keyboard_builder.button(text='Выбрать цель')
    keyboard_builder.adjust(1)

    return keyboard_builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Нажми кнопку,чтобы перейти к выбору цели'
        )
