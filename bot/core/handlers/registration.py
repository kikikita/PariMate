from aiogram import Router, F
from aiogram.types import Message
from core.keyboards.inline import sex_kb, category_kb, profile, sport_type_kb
from core.utils.states import Registration, Sport
from aiogram.fsm.context import FSMContext
from ..database.bd import bd_interaction


router = Router()


@router.message(F.text == 'Найти мотивацию')
async def reg_start(message: Message, state: FSMContext):
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
    await state.set_state(Registration.category)
    await message.answer('Цель из какой категории ты хочешь достичь?',
                         reply_markup=category_kb())


@router.message(Registration.sex)
async def incorrect_reg_sex(message: Message, state: FSMContext):
    await message.answer('Выбери один из вариантов', reply_markup=sex_kb())


@router.message(Registration.category,
                F.text.casefold().in_(['спорт', 'питание', 'распорядок дня']))
async def reg_category(message: Message, state: FSMContext):
    await state.update_data(category=message.text)
    data = await state.get_data()
    await state.clear()

    if message.text.lower() == 'спорт':
        await state.set_state(Sport.sport_type)
        await message.answer('Выбери вид спорта, либо укажи свой',
                             reply_markup=sport_type_kb())
    else:
        registration_text = []
        [
            registration_text.append(f'{k}:{v}')
            for k, v in data.items()
        ]
        await message.answer('\n'.join(registration_text))
    
    await bd_interaction(data)


@router.message(Registration.category)
async def incorrect_reg_category(message: Message, state: FSMContext):
    await message.answer('Выбери один из вариантов',
                         reply_markup=category_kb())
