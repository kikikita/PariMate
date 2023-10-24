from aiogram import Router, F
from aiogram.types import Message
from core.keyboards.inline import profile, category_kb, healh_kb
from core.utils.states import Habit
from aiogram.fsm.context import FSMContext


router = Router()


@router.message(Habit.habit_healh, F.text.casefold().in_(
        ['заниматься спортом', 'правильно питаться', 'пить воду',
         'принимать добавки', 'делать зарядку', 'гулять', 'назад']))
async def healh_choice(message: Message, state: FSMContext):
    if message.text in 'Назад':
        await message.answer('Выбери категорию привычек:',
                             reply_markup=category_kb())
        await state.set_state(Habit.habit_category)

    # elif message.text in 'Занятия спортом':
    #     await state.update_data(healh_choice=message.text)
    #     await message.answer('Выбери вид спорта, которым хочешь заниматься,'+
    #                          'либо укажи свой:',
    #                          reply_markup=sport_type_kb())
    #     await state.set_state(Health.sport_type)
    else:
        await state.update_data(habit_choice=message.text)
        await state.set_state(Habit.habit_frequency)
        await message.answer('Сколько раз неделю ты готов ' +
                             f'{message.text.lower()}?' +
                             '\nУкажи число дней в неделю:')


@router.message(Habit.habit_healh)
async def incorrect_healh_choice(message: Message, state: FSMContext):
    await message.answer('Выбери один из вариантов',
                         reply_markup=healh_kb())


# @router.message(Health.sport_type)
# async def sport_type(message: Message, state: FSMContext):
#     if message.text in 'Назад':
#         await message.answer('Выбери категорию привычек:',
#                              reply_markup=healh_kb())
#         await state.set_state(Health.health_choice)
#     else:
#         await state.set_state(Registration.category)
#         await state.update_data(sport_type=message.text)
#         await message.answer(f'Ты выбрал вид спорта: {message.text}')
#         await message.answer('Сколько раз в неделю ты готов заниматься?' +
#                              ' Укажи число дней в неделю')
#         await state.set_state(Health.frequency)


@router.message(Habit.habit_frequency)
async def sport_frequency(message: Message, state: FSMContext):
    if message.text.isdigit() and 1 <= int(message.text) <= 7:
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
            reply_markup=profile(['Фотоочет', 'Текст']))
    else:
        await message.answer('Введи реальное значение!')


@router.message(Habit.habit_report, F.text.casefold().in_(['фотоочет',
                                                          'текст']))
async def sport_report(message: Message, state: FSMContext):
    await state.update_data(sport_report=message.text)
    if message.text == 'Текст':
        await message.answer(
            'Хорошо! Без фотографий мы не сможем зачислять тебе баллы,' +
            ' но ты все еще сможешь пользоваться приложением с напарником.' +
            ' Он также не будет присылать фотографии')

    await message.answer('Найдем тебе напарника!')
    data = await state.get_data()
    await state.clear()
    registration_text = []
    [
        registration_text.append(f'{k}:{v}')
        for k, v in data.items()
    ]
    await message.answer('\n'.join(registration_text))


@router.message(Habit.habit_report)
async def incorrect_sport_report(message: Message, state: FSMContext):
    await message.answer('Выбери один из вариантов',
                         reply_markup=profile(['Фотоочет', 'Текст']))
