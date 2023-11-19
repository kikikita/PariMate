from aiogram import Router, F
from aiogram.types import Message
from core.keyboards.reply import main_menu_kb, category_kb, health_kb, \
    education_kb, productivity_kb, frequency_kb, report_kb, mate_kb, pari_find
from core.utils.states import Habit
from aiogram.fsm.context import FSMContext
import datetime as dt
from core.database.bd import bd_habit_update, bd_mate_find, bd_user_select, \
    bd_status_clear, bd_chat_update, bd_chat_delete
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from core.filters.chat_type import ChatTypeFilter


router = Router()
router.message.filter(
    ChatTypeFilter(chat_type=["private"])
)


@router.message(Habit.habit_category,
                F.text.casefold().in_(['здоровье и спорт',
                                       'обучение и развитие',
                                       'личная продуктивность',
                                       'назад']))
async def reg_category(message: Message, state: FSMContext):
    await state.update_data(habit_category=message.text)
    await state.set_state(Habit.habit_choice)

    if message.text.lower() == 'здоровье и спорт':
        await message.answer('Выбери желаемую привычку:',
                             reply_markup=health_kb())

    elif message.text.lower() == 'обучение и развитие':
        await message.answer('Выбери желаемую привычку:',
                             reply_markup=education_kb())

    elif message.text.lower() == 'личная продуктивность':
        await message.answer('Выбери желаемую привычку:',
                             reply_markup=productivity_kb())

    else:
        await state.clear()
        await message.answer('Главное меню',
                             reply_markup=main_menu_kb())


@router.message(Habit.habit_category)
async def incorrect_reg_category(message: Message, state: FSMContext):
    await message.answer('Выбери один из вариантов',
                         reply_markup=category_kb())


@router.message(Habit.habit_choice, F.text.casefold().in_(
        ['заниматься спортом', 'правильно питаться', 'пить воду',
         'принимать добавки', 'делать зарядку', 'гулять',
         'изучать новый навык', 'читать', 'проходить учебный курс',
         'вести дневник', 'изучать новый язык', 'медитировать',
         'соблюдать режим сна', 'планировать задачи на день',
         'проводить меньше времени в телефоне', 'назад']))
async def habit_choice(message: Message, state: FSMContext):
    if message.text in 'Назад':
        await message.answer('Выбери категорию привычек:',
                             reply_markup=category_kb())
        await state.set_state(Habit.habit_category)

    else:
        await state.update_data(habit_choice=message.text)
        await state.set_state(Habit.habit_frequency)
        await message.answer('Сколько раз неделю ты готов ' +
                             f'{message.text.lower()}?' +
                             '\nУкажи число дней в неделю:',
                             reply_markup=frequency_kb())


@router.message(Habit.habit_choice)
async def incorrect_healh_choice(message: Message, state: FSMContext):
    data = await state.get_data()
    if data['habit_category'] == "Здоровье и спорт":
        await message.answer('Выбери один из вариантов',
                             reply_markup=health_kb())
    elif data['habit_category'] == "Обучение и развитие":
        await message.answer('Выбери один из вариантов',
                             reply_markup=education_kb())
    else:
        await message.answer('Выбери один из вариантов',
                             reply_markup=productivity_kb())


@router.message(Habit.habit_frequency)
async def sport_frequency(message: Message, state: FSMContext):
    if message.text in 'Назад':
        data = await state.get_data()
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

    elif message.text.isdigit() and 1 <= int(message.text) <= 7:
        await state.update_data(habit_frequency=int(message.text))
        await state.set_state(Habit.habit_report)
        await message.answer(
            '\nКак бы ты хотел подтверждать выполнение привычки?' +
            '\n\nПримечение! \n- Выбирая "Фотоотчет", ты соглашаешься ' +
            'отправлять фото, подтверждающее выполнение выбранной' +
            f' привычки {message.text} раз(-а) в неделю. ' +
            'Ты также сможешь подтверждать или опровергать фотоотчеты ' +
            'других пользователей, получать баллы за завершение этапов ' +
            'и выполнение тренировок.'
            '\n- Выбирая "Текст", ты соглашаешься  подтверждать, ' +
            f'выполнение выполнение привычки {message.text} раз в неделю ' +
            'в виде тектового чек-листа. Баллы за выполнение тренировок ' +
            'и завершение этапов НЕ начисляются.',
            reply_markup=report_kb())
    else:
        await message.answer('Введи реальное значение!',
                             reply_markup=frequency_kb())


@router.message(Habit.habit_report,
                F.text.casefold().in_(['фотоотчет', 'текст', 'назад']))
async def sport_report(message: Message, state: FSMContext):
    if message.text in 'Назад':
        data = await state.get_data()
        await message.answer('Сколько раз неделю ты готов ' +
                             f'{data["habit_choice"].lower()}?' +
                             '\nУкажи число дней в неделю:',
                             reply_markup=frequency_kb())
        await state.set_state(Habit.habit_frequency)
    else:
        await state.update_data(habit_report=message.text)
        if message.text == 'Текст':
            await message.answer(
                'Хорошо! Без фотографий мы не сможем зачислять тебе баллы,' +
                ' но ты также можешь пользоваться приложением с напарником.' +
                ' Он также не будет присылать фотографии')
        data = await state.get_data()
        pari_start = dt.datetime.now().strftime("%d/%m/%y")
        pari_end = (dt.datetime.now() + dt.timedelta(days=7))\
            .strftime("%d/%m/%y")
        await message.answer(
            f'Итак, твоя цель на неделю c {pari_start} по {pari_end}:' +
            f'\n{data["habit_choice"]} {data["habit_frequency"]} раз(-а). ' +
            f'Способ подтверждения: {message.text.lower()}' +
            '\n\nДля того чтобы у тебя получилось выполнить данную цель,' +
            'мы подберем тебе напарника со схожей задачей.')
        await message.answer(
            'С напарником какого пола ты бы хотел заключить пари?',
            reply_markup=mate_kb())
        await state.set_state(Habit.habit_mate_sex)


@router.message(Habit.habit_report)
async def incorrect_sport_report(message: Message, state: FSMContext):
    await message.answer('Выбери один из вариантов',
                         reply_markup=report_kb())


@router.message(Habit.habit_mate_sex)
async def habit_mate_sex(message: Message, state: FSMContext,
                         scheduler: AsyncIOScheduler):
    if message.text in 'Назад':
        await message.answer(
            '\nКак бы ты хотел подтверждать выполнение привычки?' +
            '\n\nПримечение! \n- Выбирая "Фотоотчет", ты соглашаешься ' +
            'отправлять фото, подтверждающее выполнение выбранной' +
            f' привычки {message.text} раз(-а) в неделю. ' +
            'Ты также сможешь подтверждать или опровергать фотоотчеты ' +
            'других пользователей, получать баллы за завершение этапов ' +
            'и выполнение тренировок.'
            '\n- Выбирая "Текст", ты соглашаешься  подтверждать, ' +
            f'выполнение выполнение привычки {message.text} раз в неделю ' +
            'в виде тектового чек-листа. Баллы за выполнение тренировок ' +
            'и завершение этапов НЕ начисляются.',
            reply_markup=report_kb())
        await state.set_state(Habit.habit_report)
    else:
        await message.answer('Ищем партнера по привычке...',
                             reply_markup=pari_find())
        await state.update_data(habit_mate_sex=message.text)
        await state.update_data(mate_find=datetime.now())
        data = await state.get_data()
        await bd_habit_update(message.from_user.id, data)
        await state.set_state(Habit.mate_find)
        await pari_mate_find(message, state, scheduler)


@router.message(Habit.mate_find)
async def pari_mate_find(message: Message, state: FSMContext,
                         scheduler: AsyncIOScheduler):
    data = await state.get_data()
    if message.text == 'Отменить поиск':
        await message.answer('Поиск отменен')
        await bd_status_clear(message.from_user.id)
        await message.answer(
            'С напарником какого пола ты бы хотел заключить пари?',
            reply_markup=mate_kb())
        await state.set_state(Habit.habit_mate_sex)
        scheduler.remove_job(f'mate_find_{message.from_user.id}')

# 'No job by the id of mate_cancel_323718009 was found'
        scheduler.remove_job(f'mate_cancel_{message.from_user.id}')
        await bd_chat_delete(message.from_user.id)

    elif message.text == 'Отказаться':
        await message.answer('Вы отказались от пари')
        await bd_status_clear(message.from_user.id)
        await message.answer(
            'С напарником какого пола ты бы хотел заключить пари?',
            reply_markup=mate_kb())
        await state.set_state(Habit.habit_mate_sex)
        scheduler.remove_job(f'mate_find_{message.from_user.id}')
        scheduler.remove_job(f'mate_cancel_{message.from_user.id}')
        await bd_chat_delete(message.from_user.id)

    elif message.text == 'Подтвердить пари':
        scheduler.add_job(bd_chat_update, trigger='interval',
                          seconds=5, id=f'chat_find_{message.from_user.id}',
                          kwargs={'message': message,
                                  'mate_id': data['mate_id'],
                                  'scheduler': scheduler,
                                  'state': state})
        await message.answer('Ожидаем подтверждение от напарника...')
        await state.set_state(Habit.remove_confirm)
        # await state.clear()

    else:
        sex = (await bd_user_select(message.from_user.id))['sex']

        scheduler.add_job(bd_mate_find, trigger='interval',
                          seconds=5, id=f'mate_find_{message.from_user.id}',
                          kwargs={'message': message,
                                  'values': data,
                                  'sex': sex,
                                  'scheduler': scheduler,
                                  'state': state})


@router.message(Habit.remove_confirm,
                F.text.casefold().in_(['отказаться', 'отменить поиск']))
async def remove_confirm(message: Message, state: FSMContext,
                         scheduler: AsyncIOScheduler):
    scheduler.remove_all_jobs()
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
