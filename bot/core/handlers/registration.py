from aiogram import Bot
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from core.keyboards.inline import (
    sex_kb, category_kb, pari_choice, pari_find)
from core.utils.states import Registration, Habit
from aiogram.fsm.context import FSMContext
from ..database.bd import bd_interaction, bd_user_select, bd_habit_clear
from core.filters.chat_type import ChatTypeFilter
from core.handlers.profile import get_profile
from core.handlers.find import find_cancel


router = Router()
router.message.filter(
    ChatTypeFilter(chat_type=["private"])
)


# ИЗМЕНЕНИЕ ДАННЫХ О ПРИВЫЧКЕ
@router.callback_query(F.data.startswith("start_change"))
async def start_change(callback: CallbackQuery, state: FSMContext):
    await bd_habit_clear(callback.from_user.id)
    await reg_start(callback, state)


@router.callback_query(F.data.startswith("start"))
async def reg_start(callback: CallbackQuery, state: FSMContext):
    result = await bd_user_select(callback.from_user.id)
    if result is not False:
        # ЕСЛИ ЧЕЛ НЕ ИЩЕТ ПАРИ НО У НЕГО ЕСТЬ ПРИВЫЧКА
        if result['habit_notification_time']\
                and result['time_find_start'] is None\
                and result['pari_mate_id'] is None\
                and result['time_pari_start'] is None:
            print('МЫ ТУТ')
            await find_cancel(callback)
        # ЕСЛИ ЧЕЛ НЕ ИЩЕТ ПАРИ И У НЕГО НЕТ ПРИВЫЧКИ
        elif result['habit_notification_time'] is None\
            and result['pari_mate_id'] is None\
                and result['time_find_start'] is None:
            await state.set_state(Habit.habit_category)
            await callback.message.edit_text(
                'Выбери категорию привычек:',
                reply_markup=category_kb())
        # ЕСЛИ ЧЕЛ ИЩЕТ ПАРИ И ЕМУ НАШЕЛСЯ НАПАРНИК
        elif result['pari_mate_id'] is not None\
                and result['time_pari_start'] is None:
            mate = await bd_user_select(result['pari_mate_id'])
            await state.update_data(mate_id=mate["user_id"])
            await callback.message.answer(
                'Мы нашли для тебя напарника, и он ожидает подверждения!')
            await callback.message.answer(
                'Партнер по привычке найден:' +
                f'\n{mate["name"]}, {mate["age"]}' +
                f'\nЦель: {mate["habit_choice"].lower()} ' +
                f'{mate["habit_frequency"]} раз в неделю.',
                reply_markup=pari_choice())
        # ЕСЛИ ЧЕЛ ИЩЕТ ПАРИ И У НЕГО НЕТ НАПАРНИКА
        elif result['pari_mate_id'] is None\
                and result['time_find_start']:
            await callback.message.edit_text(
                '⏳ Подбираем партнера по привычке...' +
                '\n✉ Сообщим, как будет готово',
                reply_markup=pari_find())
        else:
            await callback.message.answer(
                'У тебя уже есть активное пари!' +
                '\nНайти новое можно только после завершения текущего')
    else:
        await state.set_state(Registration.name)
        await callback.message.answer(
            'Давай начнем, введи свое имя')
    await callback.answer()


@router.message(Registration.name, F.text)
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


@router.callback_query(Registration.sex,
                       F.data.startswith("sex_"))
async def reg_sex(callback: CallbackQuery, state: FSMContext, bot: Bot):
    action = callback.data.split("_")[1]
    await state.update_data(sex=action)
    data = await state.get_data()
    user = await bd_interaction(callback.from_user.id, data,
                                callback.from_user.username)
    await state.clear()
    await state.set_state(Habit.habit_category)
    if user is not None:
        await callback.message.answer(
            'Данные обновлены')
        await get_profile(callback, state, bot)
    else:
        await callback.message.delete_reply_markup()
        await callback.message.answer(
            'Выбери категорию привычек:',
            reply_markup=category_kb())
    await callback.answer()


@router.message(Registration.sex)
async def incorrect_reg_sex(message: Message, state: FSMContext):
    await message.answer('Выбери один из вариантов', reply_markup=sex_kb())
