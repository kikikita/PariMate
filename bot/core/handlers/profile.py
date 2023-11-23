from aiogram import Bot, Router, F
from aiogram.filters import Command
from aiogram.types import Message
from core.filters.chat_type import ChatTypeFilter
from core.keyboards.inline import profile_kb
# from aiogram.fsm.context import FSMContext
# from core.utils.states import Pari, Habit
from core.database.bd import bd_user_select


router = Router()


@router.message(Command(commands=["profile"]),
                ChatTypeFilter(chat_type=["private"]))
@router.message(F.text.casefold().in_(['профиль']))
async def get_profile(message: Message, bot: Bot):
    profile = await bd_user_select(message.from_user.id)
    if profile['habit_notification_time'] is not None:
        days_string = (str(profile["habit_notification_day"])[1:-1]
                       .replace("'", ""))
        pari = ('Не активно' if profile['time_pari_start'] is None
                else 'Активно')
        text = (
            f'Твой профиль:\n\nИмя: {profile["name"]}' +
            f'\nВозраст: {profile["age"]}\nПол: {profile["sex"]}' +
            f'\n\nПривычка: {profile["habit_choice"]}' +
            f'\nРегулярность {days_string}' +
            f'\nНапоминания: {profile["habit_notification_time"]}' +
            f'\n\nПари: {pari}')
    elif profile['sex'] is not None:
        text = (
            f'Твой профиль:\n\nИмя: {profile["name"]}' +
            f'\nВозраст: {profile["age"]}\nПол: {profile["sex"]}')
    else:
        text = 'Как тебя зовут?'
    await message.answer(text, reply_markup=profile_kb())
