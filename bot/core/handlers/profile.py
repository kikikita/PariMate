from aiogram import Bot, Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from core.filters.chat_type import ChatTypeFilter
from core.keyboards.inline import profile_kb
from core.keyboards.reply import pari_choice, profile
# from core.keyboards.reply import (
#     frequency_kb, report_kb, hours_kb)
from aiogram.fsm.context import FSMContext
from core.utils.states import Habit, Registration
from core.database.bd import bd_user_select
# from core.utils.notifications import get_date_notify


router = Router()
router.message.filter(
    ChatTypeFilter(chat_type=["private"])
)


@router.message(Command(commands=["profile"]))
@router.message(F.text.casefold().in_(['профиль']))
async def get_profile(message: Message, state: FSMContext, bot: Bot):
    profile = await bd_user_select(message.from_user.id)
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
        'Введи свое имя',
        reply_markup=profile(callback.from_user.first_name))
    await callback.answer()


# @router.callback_query(F.data == "update_notifications")
# async def get_notify(callback: CallbackQuery, state: FSMContext):
#     await state.set_state(Profile.habit_frequency)
#     await callback.message.answer(
#                         'Выбери дни недели, в которые ты хочешь получать ' +
#                         'напоминания:',
#                         reply_markup=frequency_kb())


# @router.message(Profile.habit_frequency, F.text.casefold().in_(
#         ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']))
# async def habit_day_choose(message: Message, state: FSMContext):
#     day_list = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
#     data = await state.get_data()
#     if 'habit_message' in data and data['habit_message'] is not None:
#         await data['habit_message'].delete()

#     if 'habit_frequency' not in data:
#         data['habit_frequency'] = [message.text]
#     else:
#         if message.text in data['habit_frequency']:
#             data['habit_frequency'].remove(message.text)
#         else:
#             data['habit_frequency'].append(message.text)
#     data['habit_frequency'] = sorted(data['habit_frequency'],
#                                      key=day_list.index)
#     days_string = (str(data["habit_frequency"])[1:-1].replace("'", ""))
#     await message.delete()
#     msg = await message.answer(
#         f'Ты выбрал: {days_string}',
#         reply_markup=frequency_kb(
#             'Подтвердить' if len(data['habit_frequency']) > 0 else None))
#     await state.update_data(habit_frequency=data['habit_frequency'],
#                             habit_message=msg)
#     await state.set_state(Profile.habit_frequency)


# @router.message(Profile.habit_frequency, F.text.casefold().in_([
#         'назад', 'подтвердить']))
# async def habit_frequency(message: Message, state: FSMContext, bot: Bot):
#     data = await state.get_data()
#     if message.text in 'Назад':
#         await state.clear()
#         await get_profile(message, state, bot)

#     else:
#         await state.update_data(
#             habit_notification_day=data['habit_frequency'],
#             habit_frequency=len(data['habit_frequency']),
#             habit_message=None)
#         await state.set_state(Profile.habit_notification_time)
#         await message.answer(
#             'В какое время суток присылать напоминание о привычке?',
#             reply_markup=report_kb())


# @router.message(Profile.habit_frequency)
# async def incorrect_frequency(message: Message, state: FSMContext):
#     await message.answer('Выбери дни недели',
#                          reply_markup=frequency_kb())
#     await message.delete()


# @router.message(Profile.habit_notification_time,
#                 F.text.casefold().in_(['утро', 'день', 'вечер',
#                                        'напоминания не нужны', 'назад']))
# async def habit_alarm(message: Message, state: FSMContext):
#     data = await state.get_data()
#     if message.text in 'Назад':
#         await state.update_data(habit_notification_time=[])
#         await message.answer(
#                         'Выбери дни недели, в которые ты хочешь получать ' +
#                         'напоминания:',
#                         reply_markup=frequency_kb())
#         await state.update_data(habit_frequency=[])
#         await state.set_state(Profile.habit_frequency)

#     elif message.text in ['Утро', 'День', 'Вечер']:
#         await message.answer('Выбери время',
#                              reply_markup=hours_kb(message.text))
#         await state.set_state(Profile.habit_hour)
#     else:
#         await state.update_data(habit_notification_time=message.text)
#         if 'habit_notification_time' in data\
#                 and data['habit_notification_time'] !='Напоминания не нужны':
#             notification_dates = get_date_notify(
#                 data['habit_notification_day'],
#                 data['habit_notification_time'])
#             await bd_notify_update(
#                 message.from_user.id, notification_dates,
#                 str(data['habit_notification_day']),
#                 str(data['habit_notification_time'])
#                 )
#             await message.answer('Напоминания обновлены')
#             await


# @router.message(Profile.habit_notification_time)
# async def incorrect_day_part(message: Message, state: FSMContext):
#     await message.answer(
#             'В какое время суток присылать напоминание о привычке?',
#             reply_markup=report_kb())
#     await message.delete()


# @router.message(Profile.habit_hour,
#                 F.text.casefold().in_([
#                     '6:00', '7:00', '8:00', '9:00', '10:00', '11:00',
#                     '12:00', '13:00', '14:00', '15:00', '16:00', '17:00',
#                     '18:00', '19:00', '20:00', '21:00', '22:00', '23:00',
#                     'назад']))
# async def hours_choice(message: Message, state: FSMContext):
#     if message.text == 'Назад':
#         await message.answer(
#             'В какое время суток присылать напоминание о привычке?',
#             reply_markup=report_kb()
#         )
#         await state.set_state(Habit.habit_notification_time)
#     else:
#         await state.update_data(habit_notification_time=message.text)
#         data = await state.get_data()
#         pari_start = dt.datetime.now().strftime("%d/%m/%y")
#         pari_end = (dt.datetime.now() + dt.timedelta(days=7))\
#             .strftime("%d/%m/%y")
#         days_string = (str(data["habit_notification_day"])[1:-1]
#                        .replace("'", ""))
