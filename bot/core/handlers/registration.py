from aiogram import Router, F
from aiogram.types import Message
from core.keyboards.reply import main_menu_kb, sex_kb, category_kb, profile
from core.utils.states import Registration, Habit
from aiogram.fsm.context import FSMContext
from ..database.bd import bd_interaction, bd_user_select
from core.filters.chat_type import ChatTypeFilter


router = Router()
router.message.filter(
    ChatTypeFilter(chat_type=["private"])
)


@router.message(F.text == 'Найти мотивацию')
async def reg_start(message: Message, state: FSMContext):
    result = await bd_user_select(message.from_user.id)
    if result is not False:
        if result['pari_chat_link'] is None:
            await state.set_state(Habit.habit_category)
            await message.answer('Выбери категорию привычек:',
                                 reply_markup=category_kb())
        else:
            await message.answer(
                'У тебя уже есть активное пари!' +
                '\nНайти новое можно только после завершения текущего',
                reply_markup=main_menu_kb())
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
    await bd_interaction(message.from_user.id, data)
    await state.clear()
    await state.set_state(Habit.habit_category)
    await message.answer('Выбери категорию привычек:',
                         reply_markup=category_kb())


@router.message(Registration.sex)
async def incorrect_reg_sex(message: Message, state: FSMContext):
    await message.answer('Выбери один из вариантов', reply_markup=sex_kb())
