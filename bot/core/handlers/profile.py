from aiogram import Bot, Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from core.filters.chat_type import ChatTypeFilter
from core.keyboards.inline import profile_kb, pari_choice
from aiogram.fsm.context import FSMContext
from core.utils.states import Habit, Registration
from core.database.bd import bd_user_select


router = Router()
router.message.filter(
    ChatTypeFilter(chat_type=["private"])
)


@router.message(Command(commands=["profile"]))
@router.callback_query(F.data.startswith("profile"))
# @router.message(F.text.casefold().in_(['профиль']))
async def get_profile(message: Message | CallbackQuery,
                      state: FSMContext, bot: Bot):
    await state.clear()
    user_id = message.from_user.id
    if isinstance(message, CallbackQuery):
        await message.answer()
        message = message.message
    profile = await bd_user_select(user_id)
    if profile['pari_mate_id'] is not None\
            and profile['time_pari_start'] is None:
        mate = await bd_user_select(profile['pari_mate_id'])
        await state.update_data(mate_id=mate["user_id"])
        await message.answer(
            'Мы нашли для тебя напарника, и он ожидает подверждения!')
        await message.answer(
            'Партнер по привычке найден:' +
            f'\n{mate["name"]}, {mate["age"]}' +
            f'\nЦель: {mate["habit_choice"].lower()} ' +
            f'{mate["habit_frequency"]} раз в неделю.',
            reply_markup=pari_choice())
        await state.set_state(Habit.mate_find)
    else:
        if profile['habit_notification_time'] is not None:
            days_string = (str(profile["habit_notification_day"])[1:-1]
                           .replace("'", ""))
            if profile['time_pari_start'] is not None:
                pari = 'Активно'
            elif profile['time_find_start'] is not None\
                    and profile['time_pari_start'] is None:
                pari = 'В поиске'
            else:
                pari = 'Не активно'
            text = (
                f'Твой профиль:\n\nИмя: {profile["name"]}' +
                f'\nВозраст: {profile["age"]}\nПол: {profile["sex"]}' +
                f'\n\nПривычка: {profile["habit_choice"]}' +
                f'\nРегулярность: {days_string}' +
                f'\nНапоминания: {profile["habit_notification_time"]}' +
                f'\n\nПари: {pari}')
        elif profile['sex'] is not None:
            text = (
                f'Твой профиль:\n\nИмя: {profile["name"]}' +
                f'\nВозраст: {profile["age"]}\nПол: {profile["sex"]}')
        else:
            text = 'Как тебя зовут?'
        await message.answer(
            text,
            reply_markup=profile_kb(
                1 if profile["habit_notification_time"] is not None else None))


@router.callback_query(F.data == "update_profile")
async def get_pari_report(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Registration.name)
    await callback.message.answer(
        'Введи свое имя')
    await callback.answer()
