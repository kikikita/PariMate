from aiogram import Router, F
from aiogram.types import Message
from core.keyboards.inline import profile, category_kb, health_kb, \
    report_kb, mate_kb
from core.utils.states import Habit, Health
from aiogram.fsm.context import FSMContext
import datetime as dt
from ..database.bd import bd_habit_update, bd_mate_find, bd_user_select

router = Router()


@router.message(Habit.habit_health, F.text.casefold().in_(
        ['заниматься спортом', 'правильно питаться', 'пить воду',
         'принимать добавки', 'делать зарядку', 'гулять', 'назад']))
async def healh_choice(message: Message, state: FSMContext):
    if message.text in 'Назад':
        await message.answer('Выбери категорию привычек:',
                             reply_markup=category_kb())
        await state.set_state(Habit.habit_category)

    else:
        await state.update_data(habit_choice=message.text)
        await state.set_state(Health.habit_frequency)
        await message.answer('Сколько раз неделю ты готов ' +
                             f'{message.text.lower()}?' +
                             '\nУкажи число дней в неделю:',
                             reply_markup=profile('Назад'))


@router.message(Habit.habit_health)
async def incorrect_healh_choice(message: Message, state: FSMContext):
    await message.answer('Выбери один из вариантов',
                         reply_markup=health_kb())


# @router.message(Health.habit_frequency)
# async def habit_cause(message: Message, state: FSMContext):
#     if message.text in 'Назад':
#         await message.answer('Выбери желаемую привычку:',
#                              reply_markup=health_kb())
#         await state.set_state(Habit.habit_health)
#     else:
#         if message.text.isdigit() and 1 <= int(message.text) <= 7:
#             await state.update_data(habit_frequency=int(message.text))
#             await state.set_state(Health.habit_cause)
#             data = await state.get_data()
#             await message.answer(
#                 'Что изменится в твоей жизни, если ты будешь регулярно ' +
#                 f'{data["habit_choice"].lower()}?',
#                 reply_markup=profile('Назад'))
#         else:
#             await message.answer('Введи реальное значение!',
#                                  reply_markup=profile('Назад'))


@router.message(Health.habit_frequency)
async def sport_frequency(message: Message, state: FSMContext):
    if message.text in 'Назад':
        await message.answer('Выбери желаемую привычку:',
                             reply_markup=health_kb())
        await state.set_state(Habit.habit_health)

    elif message.text.isdigit() and 1 <= int(message.text) <= 7:
        await state.update_data(habit_frequency=int(message.text))
        await state.set_state(Health.habit_report)
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
        await message.answer('Введи реальное значение!')


@router.message(Health.habit_report,
                F.text.casefold().in_(['фотоотчет', 'текст', 'назад']))
async def sport_report(message: Message, state: FSMContext):
    if message.text in 'Назад':
        data = await state.get_data()
        await message.answer('Сколько раз неделю ты готов ' +
                             f'{data["habit_choice"].lower()}?' +
                             '\nУкажи число дней в неделю:',
                             reply_markup=profile('Назад'))
        await state.set_state(Health.habit_frequency)
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
        await state.set_state(Health.habit_mate_sex)


@router.message(Health.habit_report)
async def incorrect_sport_report(message: Message, state: FSMContext):
    await message.answer('Выбери один из вариантов',
                         reply_markup=report_kb())


@router.message(Health.habit_mate_sex)
async def habit_mate_sex(message: Message, state: FSMContext):
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
        await state.set_state(Health.habit_report)
    else:
        await state.update_data(habit_mate_sex=message.text)
        data = await state.get_data()
        await bd_habit_update(message, data)
        sex = (await bd_user_select(message))['sex']
        pari_mate = await bd_mate_find(message, data, sex)
        await message.answer(
            'Партнер по привычке найден:' +
            f'\n{pari_mate["name"]}, {pari_mate["age"]}' +
            f'\nЦель: {pari_mate["habit_choice"].lower()} ' +
            f'{pari_mate["habit_frequency"]} раз в неделю.' +
            '\n\nВот ссылка на совместный чат: https://t.me/+gRd0TMWZ61JkMDAy')
