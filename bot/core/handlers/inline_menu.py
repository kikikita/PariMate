from aiogram import Router, F
from aiogram.filters import Command
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery
from core.keyboards.inline import get_keyboard_fab, get_main_menu, \
    NumbersCallbackFactory, MenuCallbackFactory
from aiogram.fsm.context import FSMContext


router = Router()


async def update_menu(message: Message):
    with suppress(TelegramBadRequest):
        await message.edit_text(
            'Категория привычки:',
            reply_markup=get_main_menu()
        )


@router.message(Command(commands=["menu2"]))
async def get_menu(message: Message, state: FSMContext):
    await message.answer(
            'Главное меню:', reply_markup=get_main_menu())


@router.callback_query(MenuCallbackFactory.filter(F.action == "habit"))
async def habit_change(
        callback: CallbackQuery
):
    await update_menu(callback.message)
    await callback.answer()


user_data = {}


async def update_num_text_fab(message: Message, new_value: int):
    with suppress(TelegramBadRequest):
        await message.edit_text(
            f"Укажите число: {new_value}",
            reply_markup=get_keyboard_fab()
        )


@router.message(Command(commands=["pari"]))
async def cmd_numbers_fab(message: Message):
    user_data[message.from_user.id] = 0
    await message.answer("Укажите число: 0", reply_markup=get_keyboard_fab())


# Нажатие на одну из кнопок: -2, -1, +1, +2
@router.callback_query(NumbersCallbackFactory.filter(F.action == "change"))
async def callbacks_num_change_fab(
        callback: CallbackQuery,
        callback_data: NumbersCallbackFactory
):
    # Текущее значение
    user_value = user_data.get(callback.from_user.id, 0)

    user_data[callback.from_user.id] = user_value + callback_data.value
    await update_num_text_fab(callback.message, user_value +
                              callback_data.value)
    await callback.answer()


# Нажатие на кнопку "подтвердить"
@router.callback_query(NumbersCallbackFactory.filter(F.action == "finish"))
async def callbacks_num_finish_fab(callback: CallbackQuery):
    # Текущее значение
    user_value = user_data.get(callback.from_user.id, 0)

    await callback.message.edit_text(f"Итого: {user_value}")
    await callback.answer()
