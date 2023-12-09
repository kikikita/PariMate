from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery
from core.keyboards.inline import (
    health_kb, education_kb, productivity_kb,
    frequency_kb, mate_kb, pari_find, hours_kb)
from core.utils.states import Habit
from aiogram.fsm.context import FSMContext
import datetime as dt
from core.database.bd import (
    bd_habit_update, bd_notify_update)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from core.filters.chat_type import ChatTypeFilter
from core.utils.notifications import get_date_notify


router = Router()
router.message.filter(
    ChatTypeFilter(chat_type=["private"])
)


@router.callback_query(F.data.startswith("habit_"))
async def reg_category(callback: CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[1]
    await state.update_data(habit_category=action,
                            callback=callback)
    await state.set_state(Habit.habit_choice)

    if action.lower() == 'здоровье и спорт':
        await callback.message.edit_text(
            'Выбери желаемую привычку, либо укажи свою:',
            reply_markup=health_kb())

    elif action.lower() == 'обучение и развитие':
        await callback.message.edit_text(
            'Выбери желаемую привычку, либо укажи свою:',
            reply_markup=education_kb())

    else:
        await callback.message.edit_text(
            'Выбери желаемую привычку, либо укажи свою:',
            reply_markup=productivity_kb())
    await callback.answer()


@router.message(Habit.habit_category)
async def incorrect_reg_category(message: Message, state: FSMContext):
    await message.delete()


@router.message(Habit.habit_choice)
async def habit_write_choice(message: Message, state: FSMContext):
    callback = (await state.get_data())['callback']
    await habit_choice(callback=callback, state=state, action=message.text)
    await message.delete()


@router.callback_query(F.data.startswith("choice_"))
async def habit_choice(callback: CallbackQuery, state: FSMContext,
                       action: Message | None = None):
    data = await state.get_data()
    if 'habit_category' not in data:
        await callback.message.delete()
        return
    if not action:
        action = callback.data.split("_")[1]
    await state.update_data(habit_choice=action,
                            habit_notification_day=[])
    await state.set_state(Habit.habit_notification_day)
    await callback.message.edit_text(
        'Выбери дни недели, в которые ты готов(-а) ' +
        f'{action.lower()}?' +
        '\n(для отмены повтори выбор)',
        reply_markup=frequency_kb(data['habit_category']))
    await callback.answer()


@router.callback_query(F.data.startswith("freq_"))
async def habit_day_choose(callback: CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[1]
    day_list = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    data = await state.get_data()
    if 'habit_category' not in data:
        await callback.message.delete()
        return
        # data = await state_fill(callback.from_user.id, state)

    if action in data['habit_notification_day']\
            and action != 'Ежедневно':
        data['habit_notification_day'].remove(action)
    elif action == 'Ежедневно'\
            and data['habit_notification_day'] != day_list:
        data['habit_notification_day'] = day_list
    elif action == 'Ежедневно'\
            and data['habit_notification_day'] == day_list:
        data['habit_notification_day'] = []
    else:
        data['habit_notification_day'].append(action)
    data['habit_notification_day'] = sorted(data['habit_notification_day'],
                                            key=day_list.index)
    days_string = (str(data["habit_notification_day"])[1:-1].replace("'", ""))

    await callback.message.edit_text(
        f'Ты выбрал: {days_string}',
        reply_markup=frequency_kb(
            data['habit_category'],
            'Подтвердить' if len(data['habit_notification_day']) > 0
            else None))
    await state.update_data(
        habit_notification_day=data['habit_notification_day'])
    await state.set_state(Habit.habit_notification_day)
    await callback.answer()


@router.callback_query(F.data.startswith("approve_freq"))
async def habit_frequency(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if 'habit_category' not in data and 'habit_choice' not in data:
        await callback.message.delete()
        return

    await state.update_data(
        habit_notification_day=data['habit_notification_day'],
        habit_frequency=len(data['habit_notification_day']),
        habit_notification_time=[])
    await state.set_state(Habit.habit_notification_time)
    await callback.message.edit_text(
        'В какое время присылать напоминание о привычке?' +
        '\n(примечание: время по МСК)',
        reply_markup=hours_kb())
    await callback.answer()


@router.message(Habit.habit_notification_day)
async def incorrect_frequency(message: Message, state: FSMContext):
    await message.answer('Выбери дни недели',
                         reply_markup=frequency_kb())
    await message.delete()


@router.callback_query(F.data.startswith("time_"))
async def habit_time_choose(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if 'habit_category' not in data and 'habit_notification_day' not in data:
        await callback.message.delete()
        return

    action = callback.data.split("_")[1]
    time_list = ['5:00', '6:00', '7:00', '8:00', '9:00', '10:00', '11:00',
                 '12:00', '13:00', '14:00', '15:00', '16:00', '17:00',
                 '18:00', '19:00', '20:00', '21:00', '22:00', '23:00', '0:00']

    if action in data['habit_notification_time']:
        data['habit_notification_time'].remove(action)
    else:
        data['habit_notification_time'].append(action)
    data['habit_notification_time'] = sorted(
        data['habit_notification_time'], key=time_list.index)
    time_string = (str(data["habit_notification_time"])[1:-1].replace("'", ""))
    await callback.message.edit_text(
        f'Ты выбрал: {time_string}',
        reply_markup=hours_kb(
            'Подтвердить' if len(data['habit_notification_time']) > 0
            else None))
    await state.update_data(
        habit_notification_time=data['habit_notification_time'])
    await state.set_state(Habit.habit_notification_time)
    await callback.answer()


@router.callback_query(Habit.habit_notification_time,
                       F.data.startswith("approve_time"))
async def hours_choice(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if 'habit_category' not in data and 'habit_notification_time' not in data\
            or data['habit_notification_time'] == []:
        await callback.message.delete()
        return

    pari_start = dt.datetime.now().strftime("%d/%m/%y")
    pari_end = (dt.datetime.now() + dt.timedelta(days=7))\
        .strftime("%d/%m/%y")
    days_string = (str(data["habit_notification_day"])[1:-1]
                   .replace("'", ""))
    time_string = (str(data["habit_notification_time"])[1:-1]
                   .replace("'", ""))
    await callback.message.edit_text(
        f'🎯 Итак, твоя цель на неделю c {pari_start} по {pari_end}:' +
        f'\n{data["habit_choice"]} в {days_string}. ' +
        f'\nВремя напоминаний: {time_string}' +
        '\n\nЧтобы поднять твой уровень мотивации, ' +
        'мы подберем тебе напарника со схожей задачей' +
        '\n❗ Важно: вы будете обмениваться с напарником фото и видео' +
        'подтверждениями внедрения привычек в свою жизнь' +
        '\n\nС напарником какого пола ты бы хотел заключить пари?',
        reply_markup=mate_kb())
    await state.set_state(Habit.habit_mate_sex)
    await callback.answer()


@router.message(Habit.habit_notification_time)
async def incorrect_day_part(message: Message, state: FSMContext):
    await message.delete()


@router.callback_query(F.data.startswith("sex_"))
async def habit_mate_sex(callback: CallbackQuery, state: FSMContext,
                         scheduler: AsyncIOScheduler, bot: Bot):
    data = await state.get_data()
    if 'habit_category' not in data:
        await callback.message.delete()
        return
    action = callback.data.split("_")[1]
    await state.update_data(habit_mate_sex=action,
                            time_find_start=datetime.now())
    data = await state.get_data()
    notification_dates = get_date_notify(
            data['habit_notification_day'],
            data['habit_notification_time'])
    await bd_notify_update(callback.from_user.id, notification_dates)
    await bd_habit_update(callback.from_user.id, data)
    await callback.message.edit_text(
        '⏳ Подбираем партнера по привычке...' +
        '\n✉ Сообщим, как будет готово',
        reply_markup=pari_find())
    await callback.answer()


@router.message(Habit.habit_mate_sex)
async def incorrect_mate_sex(message: Message, state: FSMContext):
    await state.set_state(Habit.habit_mate_sex)
    await message.delete()
