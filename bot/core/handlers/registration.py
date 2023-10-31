from aiogram import Router, F
from aiogram.types import Message
from core.keyboards.inline import \
    sex_kb, category_kb, profile, health_kb, education_kb, productivity_kb
from core.utils.states import Registration, Habit
from aiogram.fsm.context import FSMContext
from ..database.bd import bd_interaction, bd_user_check


router = Router()


@router.message(F.text == 'Найти мотивацию')
async def reg_start(message: Message, state: FSMContext):
    if await bd_user_check(message) is not False:
        await state.set_state(Habit.habit_category)
        await message.answer('Выбери категорию привычек:',
                             reply_markup=category_kb())
    else:
        await state.set_state(Registration.name)
        await message.answer(
            'Давай начнем, введи свое имя',
            reply_markup=profile(message.from_user.first_name))


@router.message(Registration.name)
async def reg_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Registration.age)
    await message.answer(f'Приятно познакомиться, {message.text}' +
                         '\nСколько тебе лет?')


@router.message(Registration.age)
async def reg_age(message: Message, state: FSMContext):
    if message.text.isdigit() and 7 < int(message.text) < 90:
        await state.update_data(age=message.text)
        await state.set_state(Registration.sex)
        await message.answer('Какого ты пола?',
                             reply_markup=sex_kb())
    else:
        await message.answer('Укажи свой реальный возраст числом!')


@router.message(Registration.sex, F.text.casefold().in_(['мужчина',
                                                         'женщина']))
async def reg_sex(message: Message, state: FSMContext):
    await state.update_data(sex=message.text)
    data = await state.get_data()
    await bd_interaction(message, data)
    await state.clear()
    await state.set_state(Habit.habit_category)
    await message.answer('Выбери категорию привычек:',
                         reply_markup=category_kb())


@router.message(Registration.sex)
async def incorrect_reg_sex(message: Message, state: FSMContext):
    await message.answer('Выбери один из вариантов', reply_markup=sex_kb())


@router.message(Habit.habit_category,
                F.text.casefold().in_(['здоровье и спорт',
                                       'обучение и развитие',
                                       'личная продуктивность']))
async def reg_category(message: Message, state: FSMContext):
    await state.update_data(habit_category=message.text)

    if message.text.lower() == 'здоровье и спорт':
        await state.set_state(Habit.habit_health)
        await message.answer('Выбери желаемую привычку:',
                             reply_markup=health_kb())

    elif message.text.lower() == 'обучение и развитие':
        await state.set_state(Habit.habit_education)
        await message.answer('Выбери желаемую привычку:',
                             reply_markup=education_kb())

    elif message.text.lower() == 'личная продуктивность':
        await state.set_state(Habit.habit_productivity)
        await message.answer('Выбери желаемую привычку:',
                             reply_markup=productivity_kb())


@router.message(Habit.habit_category)
async def incorrect_reg_category(message: Message, state: FSMContext):
    await message.answer('Выбери один из вариантов',
                         reply_markup=category_kb())
