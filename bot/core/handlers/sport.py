from aiogram import Router, F
from aiogram.types import Message
from core.keyboards.inline import profile
from core.utils.states import Sport
from aiogram.fsm.context import FSMContext


router = Router()


@router.message(Sport.sport_type)
async def sport_type(message: Message, state: FSMContext):
    await state.update_data(sport_type=message.text)
    await message.answer(f'Ты выбрал вид спорта: {message.text}')
    await message.answer('Сколько раз в неделю ты готов заниматься?' +
                         ' Укажи число дней в неделю')
    await state.set_state(Sport.frequency)


@router.message(Sport.frequency)
async def sport_frequency(message: Message, state: FSMContext):
    if message.text.isdigit() and 1 <= int(message.text) <= 7:
        await state.update_data(frequency=int(message.text))
        await state.set_state(Sport.report)
        await message.answer(
            '\nКак бы ты хотел подтверждать занятия спортом?' +
            '\n\nПримечение! \n- Выбирая "Фотоотчет", ты соглашаешься ' +
            'отправлять фото, подтверждающее твое занятие выбранным' +
            f' видом спорта {message.text} раз(-а) в неделю. ' +
            'Ты также сможешь подтверждать или опровергать фотоотчеты ' +
            'других пользователей, получать баллы за завершение этапов ' +
            'и выполнение тренировок.'
            '\n- Выбирая "Текст", ты соглашаешься  подтверждать, ' +
            f'занятия выбранным видом спорта {message.text} раз в неделю ' +
            'в виде тектового чек-листа. Баллы за выполнение тренировок ' +
            'и завершение этапов НЕ начисляются.',
            reply_markup=profile(['Фотоочет', 'Текст']))
    else:
        await message.answer('Введи реальное значение!')

# await message.answer(
#     'Ну и последний по вопрос!' +
#     '\nГотов ли ты действовать решительно+' +
#     ' и подтверждать выполнене своих тренировок фото-отчетом?' +
#     '\nПри выборе варианта "Не готов" баллы за выполнение тренировок' +
#     ' не начисляются. Подтверждение осуществляется в текстовом формате',
#     reply_markup=profile(['Готов', 'Не готов']))


@router.message(Sport.report, F.text.casefold().in_(['фотоочет',
                                                    'текст']))
async def sport_report(message: Message, state: FSMContext):
    await state.update_data(sport_report=message.text)
    if message.text == 'Текст':
        await message.answer(
            'Хорошо! Без фотографий мы не сможем зачислять тебе баллы,' +
            ' но ты все еще сможешь пользоваться приложением с напарником.' +
            ' Он также не будет присылать фотографии')

    await message.answer('Найдем тебе напарника!')
    await state.clear()


@router.message(Sport.report)
async def incorrect_sport_report(message: Message, state: FSMContext):
    await message.answer('Выбери один из вариантов',
                         reply_markup=profile(['Фотоочет', 'Текст']))
