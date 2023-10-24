from aiogram import Router, F
from aiogram.types import Message
from core.keyboards.inline import profile, category_kb, productivity_kb
from core.utils.states import Habit
from aiogram.fsm.context import FSMContext


router = Router()


@router.message(Habit.habit_productivity, F.text.casefold().in_(
        ['cоблюдать режим сна', 'планировать задачи на день',
         'проводить меньше времени в телефоне', 'назад']))
async def productivity_choice(message: Message, state: FSMContext):
    if message.text in 'Назад':
        await message.answer('Выбери категорию привычек:',
                             reply_markup=category_kb())
        await state.set_state(Habit.habit_category)

    else:
        await state.update_data(habit_choice=message.text)
        await state.set_state(Habit.habit_frequency)
        await message.answer('Сколько раз неделю ты готов ' +
                             f'{message.text.lower()}?' +
                             '\nУкажи число дней в неделю')


@router.message(Habit.habit_productivity)
async def incorrect_productivity_choice(message: Message, state: FSMContext):
    await message.answer('Выбери один из вариантов',
                         reply_markup=productivity_kb())


@router.message(Habit.habit_frequency)
async def productivity_frequency(message: Message, state: FSMContext):
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
async def productivity_report(message: Message, state: FSMContext):
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
async def incorrect_productivity_report(message: Message, state: FSMContext):
    await message.answer('Выбери один из вариантов',
                         reply_markup=profile(['Фотоочет', 'Текст']))
