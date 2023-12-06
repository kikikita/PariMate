from aiogram import Bot, Router, F
from aiogram.types import Message
from core.keyboards.reply import (
    main_menu_kb, category_kb, health_kb, education_kb, productivity_kb,
    frequency_kb, mate_kb, pari_find, hours_kb)
from core.utils.states import Habit
from aiogram.fsm.context import FSMContext
import datetime as dt
from core.database.bd import (
    bd_habit_update, bd_mate_find, bd_user_select, bd_status_clear,
    bd_chat_update, bd_chat_delete, bd_notify_update)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from core.filters.chat_type import ChatTypeFilter
from core.utils.notifications import get_date_notify
import time
import ast


router = Router()
router.message.filter(
    ChatTypeFilter(chat_type=["private"])
)


async def state_fill(user_id: int, state: FSMContext):
    data = await bd_user_select(user_id)
    data['habit_notification_day'] = ast.literal_eval(
            data['habit_notification_day'])
    data['habit_notification_time'] = ast.literal_eval(
            data['habit_notification_time'])
    await state.update_data(data)
    return data


@router.message(Habit.habit_category,
                F.text.casefold().in_(['здоровье и спорт',
                                       'обучение и развитие',
                                       'личная продуктивность',
                                       'назад']))
async def reg_category(message: Message, state: FSMContext):
    await state.update_data(habit_category=message.text)
    await state.set_state(Habit.habit_choice)

    if message.text.lower() == 'здоровье и спорт':
        await message.answer('Выбери желаемую привычку, либо укажи свою:',
                             reply_markup=health_kb())

    elif message.text.lower() == 'обучение и развитие':
        await message.answer('Выбери желаемую привычку, либо укажи свою:',
                             reply_markup=education_kb())

    elif message.text.lower() == 'личная продуктивность':
        await message.answer('Выбери желаемую привычку, либо укажи свою:',
                             reply_markup=productivity_kb())

    else:
        await state.clear()
        await message.answer('Главное меню',
                             reply_markup=main_menu_kb())


@router.message(Habit.habit_category)
async def incorrect_reg_category(message: Message, state: FSMContext):
    await message.answer('Выбери один из вариантов',
                         reply_markup=category_kb())


# @router.message(Habit.habit_choice, F.text.casefold().in_(
#         ['заниматься спортом', 'правильно питаться', 'пить воду',
#          'принимать добавки', 'делать зарядку', 'гулять',
#          'изучать новый навык', 'читать', 'проходить учебный курс',
#          'вести дневник', 'изучать новый язык', 'медитировать',
#          'соблюдать режим сна', 'планировать задачи на день',
#          'проводить меньше времени в телефоне', 'назад']))
@router.message(Habit.habit_choice, F.text)
async def habit_choice(message: Message, state: FSMContext):
    if message.text in 'Назад':
        await message.answer('Выбери категорию привычек:',
                             reply_markup=category_kb())
        await state.set_state(Habit.habit_category)

    else:
        await state.update_data(habit_choice=message.text)
        await state.set_state(Habit.habit_notification_day)
        await message.answer('Выбери дни недели, в которые ты готов(-а) ' +
                             f'{message.text.lower()}?' +
                             '\n(для отмены повтори выбор)',
                             reply_markup=frequency_kb())


# @router.message(Habit.habit_choice)
# async def incorrect_healh_choice(message: Message, state: FSMContext):
#     data = await state.get_data()
#     if data['habit_category'] == "Здоровье и спорт":
#         await message.answer('Выбери один из вариантов',
#                              reply_markup=health_kb())
#     elif data['habit_category'] == "Обучение и развитие":
#         await message.answer('Выбери один из вариантов',
#                              reply_markup=education_kb())
#     else:
#         await message.answer('Выбери один из вариантов',
#                              reply_markup=productivity_kb())


@router.message(Habit.habit_notification_day, F.text.casefold().in_(
        ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс', 'ежедневно']))
async def habit_day_choose(message: Message, state: FSMContext):
    day_list = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    data = await state.get_data()
    if 'habit_category' not in data:
        data = await state_fill(message.from_user.id, state)

    if 'habit_message' in data and data['habit_message'] is not None:
        await data['habit_message'].delete()

    if 'habit_notification_day' not in data:
        if message.text == 'Ежедневно':
            data['habit_notification_day'] = day_list
        else:
            data['habit_notification_day'] = [message.text]
    else:
        if message.text in data['habit_notification_day']\
                and message.text != 'Ежедневно':
            data['habit_notification_day'].remove(message.text)
        elif message.text == 'Ежедневно'\
                and data['habit_notification_day'] != day_list:
            data['habit_notification_day'] = day_list
        elif message.text == 'Ежедневно'\
                and data['habit_notification_day'] == day_list:
            data['habit_notification_day'] = []
        else:
            data['habit_notification_day'].append(message.text)
    data['habit_notification_day'] = sorted(data['habit_notification_day'],
                                            key=day_list.index)
    days_string = (str(data["habit_notification_day"])[1:-1].replace("'", ""))
    await message.delete()
    msg = await message.answer(
        f'Ты выбрал: {days_string}',
        reply_markup=frequency_kb(
            'Подтвердить' if len(data['habit_notification_day']) > 0
            else None))
    await state.update_data(
        habit_notification_day=data['habit_notification_day'],
        habit_message=msg)
    await state.set_state(Habit.habit_notification_day)


@router.message(Habit.habit_notification_day, F.text.casefold().in_([
        'назад', 'подтвердить']))
async def habit_frequency(message: Message, state: FSMContext):
    data = await state.get_data()
    if 'habit_category' not in data:
        data = await state_fill(message.from_user.id, state)

    if message.text in 'Назад':
        if data['habit_category'] == "Здоровье и спорт":
            await message.answer('Выбери один из вариантов',
                                 reply_markup=health_kb())
        elif data['habit_category'] == "Обучение и развитие":
            await message.answer('Выбери один из вариантов',
                                 reply_markup=education_kb())
        else:
            await message.answer('Выбери один из вариантов',
                                 reply_markup=productivity_kb())
        await state.set_state(Habit.habit_choice)
        await state.update_data(habit_notification_day=[])

    else:
        await state.update_data(
            habit_notification_day=data['habit_notification_day'],
            habit_frequency=len(data['habit_notification_day']),
            habit_message=None)
        await state.set_state(Habit.habit_notification_time)
        await message.answer(
            'В какое время присылать напоминание о привычке?' +
            '\n(примечание: время по МСК)',
            reply_markup=hours_kb())


@router.message(Habit.habit_notification_day)
async def incorrect_frequency(message: Message, state: FSMContext):
    await message.answer('Выбери дни недели',
                         reply_markup=frequency_kb())
    await message.delete()


@router.message(
        Habit.habit_notification_time,
        F.text.casefold().in_([
            '5:00', '6:00', '7:00', '8:00', '9:00', '10:00', '11:00',
            '12:00', '13:00', '14:00', '15:00', '16:00', '17:00',
            '18:00', '19:00', '20:00', '21:00', '22:00', '23:00', '0:00']))
async def habit_time_choose(message: Message, state: FSMContext):
    time_list = ['5:00', '6:00', '7:00', '8:00', '9:00', '10:00', '11:00',
                 '12:00', '13:00', '14:00', '15:00', '16:00', '17:00',
                 '18:00', '19:00', '20:00', '21:00', '22:00', '23:00', '0:00']
    data = await state.get_data()
    if 'habit_category' not in data:
        data = await state_fill(message.from_user.id, state)

    if 'habit_message' in data and data['habit_message'] is not None:
        await data['habit_message'].delete()

    if 'habit_notification_time' not in data:
        data['habit_notification_time'] = [message.text]
    else:
        if message.text in data['habit_notification_time']:
            data['habit_notification_time'].remove(message.text)
        else:
            data['habit_notification_time'].append(message.text)
    data['habit_notification_time'] = sorted(
        data['habit_notification_time'], key=time_list.index)
    time_string = (str(data["habit_notification_time"])[1:-1].replace("'", ""))
    await message.delete()
    msg = await message.answer(
        f'Ты выбрал: {time_string}',
        reply_markup=hours_kb(
            'Подтвердить' if len(data['habit_notification_time']) > 0
            else None))
    await state.update_data(
        habit_notification_time=data['habit_notification_time'],
        habit_message=msg)
    await state.set_state(Habit.habit_notification_time)


@router.message(Habit.habit_notification_time,
                F.text.casefold().in_(['подтвердить', 'назад']))
async def hours_choice(message: Message, state: FSMContext):
    data = await state.get_data()
    if 'habit_category' not in data:
        data = await state_fill(message.from_user.id, state)
    if message.text == 'Назад':
        if 'habit_choice' not in data:
            data = await bd_user_select(message.from_user.id)
        await state.update_data(habit_notification_time=[])
        await message.answer('Выбери дни недели, в которые ты готов(-а) ' +
                             f'{data["habit_choice"]}?',
                             reply_markup=frequency_kb())
        await state.update_data(habit_frequency=[])
        await state.set_state(Habit.habit_notification_day)
    else:
        # await state.update_data(
        #     habit_notification_time=data['habit_notification_time'])
        pari_start = dt.datetime.now().strftime("%d/%m/%y")
        pari_end = (dt.datetime.now() + dt.timedelta(days=7))\
            .strftime("%d/%m/%y")
        days_string = (str(data["habit_notification_day"])[1:-1]
                       .replace("'", ""))
        time_string = (str(data["habit_notification_time"])[1:-1]
                       .replace("'", ""))
        await message.answer(
            f'Итак, твоя цель на неделю c {pari_start} по {pari_end}:' +
            f'\n{data["habit_choice"]} в {days_string}. ' +
            f'\nВремя напоминаний: {time_string}' +
            '\n\nДля того чтобы у тебя получилось выполнить данную цель,' +
            'мы подберем тебе напарника со схожей задачей' +
            '\n!Важно: вы будете обмениваться с напарником фото и видео' +
            'подтверждениями внедрения привычек в свою жизнь')
        time.sleep(0.5)
        await message.answer(
            'С напарником какого пола ты бы хотел заключить пари?',
            reply_markup=mate_kb())
        await state.set_state(Habit.habit_mate_sex)


@router.message(Habit.habit_notification_time)
async def incorrect_day_part(message: Message, state: FSMContext):
    await message.answer(
            'В какое время присылать напоминание о привычке?',
            reply_markup=hours_kb())
    await message.delete()


@router.message(Habit.habit_mate_sex, F.text.casefold().in_(
        ['мужчина', 'женщина', 'не имеет значения', 'назад']))
async def habit_mate_sex(message: Message, state: FSMContext,
                         scheduler: AsyncIOScheduler, bot: Bot):
    if message.text in 'Назад':
        await message.answer(
                'В какое время присылать напоминание о привычке?' +
                '\n(примечание: время по МСК)',
                reply_markup=hours_kb())
        await state.set_state(Habit.habit_notification_time)
    else:
        data = await state.get_data()
        if 'habit_category' not in data:
            data = await state_fill(message.from_user.id, state)
        await state.update_data(habit_mate_sex=message.text,
                                time_find_start=datetime.now())
        data = await state.get_data()
        notification_dates = get_date_notify(
                data['habit_notification_day'],
                data['habit_notification_time'])
        await bd_notify_update(message.from_user.id, notification_dates)

        await message.answer('Ищем партнера по привычке...',
                             reply_markup=pari_find())
        # if 'habit_category' in data:
        await bd_habit_update(message.from_user.id, data)
        # else:
        #     await bd_time_find_update(message.from_user.id)
        await state.set_state(Habit.mate_find)
        await pari_mate_find(message, state, scheduler, bot)


@router.message(Habit.habit_mate_sex)
async def incorrect_mate_sex(message: Message, state: FSMContext):
    await message.answer(
            'С напарником какого пола ты бы хотел заключить пари?',
            reply_markup=mate_kb())
    await state.set_state(Habit.habit_mate_sex)


@router.message(Habit.mate_find)
async def pari_mate_find(message: Message, state: FSMContext,
                         scheduler: AsyncIOScheduler, bot: Bot):
    data = await bd_user_select(message.from_user.id)
    if message.text == 'Отменить поиск':
        await message.answer('Поиск отменен')
        await bd_status_clear(message.from_user.id)
        await message.answer(
            'С напарником какого пола ты бы хотел заключить пари?',
            reply_markup=mate_kb())
        await state.set_state(Habit.habit_mate_sex)
        get_find_job = scheduler.get_job(f'mate_find_{message.from_user.id}')
        get_cncl_job = scheduler.get_job(f'mate_cancel_{message.from_user.id}')
        if get_find_job and get_cncl_job:
            scheduler.remove_job(f'mate_find_{message.from_user.id}')
            scheduler.remove_job(f'mate_cancel_{message.from_user.id}')
        elif get_find_job and not get_cncl_job:
            scheduler.remove_job(f'mate_find_{message.from_user.id}')
        elif not get_find_job and get_cncl_job:
            scheduler.remove_job(f'mate_cancel_{message.from_user.id}')
        else:
            pass

    elif message.text == 'Отказаться':
        await message.answer('Вы отказались от пари')
        await bd_status_clear(message.from_user.id)
        await message.answer(
            'С напарником какого пола ты бы хотел заключить пари?',
            reply_markup=mate_kb())
        await state.set_state(Habit.habit_mate_sex)
        await bd_chat_delete(message.from_user.id)
        get_find_job = scheduler.get_job(f'mate_find_{message.from_user.id}')
        get_cncl_job = scheduler.get_job(f'mate_cancel_{message.from_user.id}')
        if get_find_job and get_cncl_job:
            scheduler.remove_job(f'mate_find_{message.from_user.id}')
            scheduler.remove_job(f'mate_cancel_{message.from_user.id}')
        elif get_find_job and not get_cncl_job:
            scheduler.remove_job(f'mate_find_{message.from_user.id}')
        elif not get_find_job and get_cncl_job:
            scheduler.remove_job(f'mate_cancel_{message.from_user.id}')
        else:
            pass

    elif message.text == 'Подтвердить пари':
        get_job = scheduler.get_job(f'chat_find_{message.from_user.id}')
        if not get_job:
            scheduler.add_job(
                bd_chat_update, trigger='interval',
                seconds=5, id=f'chat_find_{message.from_user.id}',
                kwargs={'user_id': message.from_user.id,
                        'mate_id': data['pari_mate_id'],
                        'scheduler': scheduler,
                        'state': state,
                        'bot': bot})
        await message.answer('Ожидаем подтверждение от напарника...')
        await state.set_state(Habit.remove_confirm)

    else:
        get_job = scheduler.get_job(f'mate_find_{message.from_user.id}')
        if not get_job:
            scheduler.add_job(
                bd_mate_find, trigger='interval',
                seconds=1, id=f'mate_find_{message.from_user.id}',
                kwargs={'message': message,
                        'scheduler': scheduler,
                        'state': state,
                        'bot': bot})


@router.message(Habit.remove_confirm,
                F.text.casefold().in_(['отказаться', 'отменить поиск']))
async def remove_confirm(message: Message, state: FSMContext,
                         scheduler: AsyncIOScheduler):
    get_job = scheduler.get_job(f'mate_cancel_{message.from_user.id}')
    if get_job:
        scheduler.remove_job(f'mate_cancel_{message.from_user.id}')
    await bd_status_clear(message.from_user.id)
    await bd_chat_delete(message.from_user.id)
    await message.answer('Вы отказались от пари')
    await message.answer(
        'С напарником какого пола ты бы хотел заключить пари?',
        reply_markup=mate_kb())
    await state.set_state(Habit.habit_mate_sex)


@router.message(Habit.remove_confirm)
async def incorrect_remove_confirm(message: Message, state: FSMContext):
    if message.text == 'Подтвердить пари':
        await message.answer('Вы уже подтвердили пари')
    await message.answer('Ожидаем подтверждение от напарника...')
