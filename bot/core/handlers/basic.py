from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from core.keyboards.inline import get_start_kb, get_main_menu
from aiogram.fsm.context import FSMContext
from core.filters.chat_type import ChatTypeFilter


router = Router()


@router.message(Command(commands=["start"]),
                ChatTypeFilter(chat_type=["private"]))
async def get_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
            f'Привет, {message.from_user.first_name}!' +
            '\nДобро пожаловать в PariMate! Здесь ты найдешь мотивацию 💪' +
            ' и сможешь соревноваться с людьми в достижении своих целей.'
            '\nВыбирай желаемую привычку, которую хочешь развить, а мы'
            ' подберем тебе оппонента со схожей целью и расписанием 🕑.'
            '\nВперед к новым победам и достижениям !',
            reply_markup=get_start_kb()
            )


@router.message(Command(commands=["menu"]),
                ChatTypeFilter(chat_type=["private"]))
@router.callback_query(
    F.data.startswith("menu"), ChatTypeFilter(chat_type=["private"]))
async def get_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
            'Главное меню',
            reply_markup=get_main_menu()
            )


@router.message(Command(commands=["menu", 'profile']),
                ChatTypeFilter(chat_type=["group", "supergroup"]))
async def get_group_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        'В групповом чате доступны следующие команды:' +
        '\n\n/pari -> Управление пари'
        '\n/help -> Помощь'
        '\n\nЧтобы получить доступ к полному меню, ' +
        'напиши эту команду в чате с ботом')


@router.message(Command(commands=["help"]),
                ChatTypeFilter(chat_type=["group", "supergroup"]))
@router.message(F.text.casefold().in_(['помощь']),
                ChatTypeFilter(chat_type=["group", "supergroup"]))
async def get_info(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
            '/pari -> доступный функционал:' +
            '\n\n🔘 Досрочно завершить пари' +
            '\n(досрочное завершения пари)'
            '\n🔘 Перейти в совместный чат' +
            '\n(кнопка-ссылка в чат с напарником)'
            '\n🔘 Отчеты напарника' +
            '\n(проверка новых отчетов напарника)' +
            '\n🔘 Подтвердить выполнение привычки ' +
            '\n(загрузка отчетов о привычках, ' +
            'формат: фото/видео/кружочки/текст)' +
            '\n\nПо вопросам работы бота: @kikikita1337')


@router.message(Command(commands=["help"]),
                ChatTypeFilter(chat_type=["private"]))
@router.message(F.text.casefold().in_(['помощь']),
                ChatTypeFilter(chat_type=["private"]))
async def get_private_info(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
            '/menu -> главное меню:' +
            '\n\n🔘 Найти мотивацию' +
            '\n(поиск напарника по привычки)' +
            '\n🔘 Мои пари' +
            '\n(раздел с активным пари)' +
            '\n🔘 Профиль' +
            '\n(редактирование профиля)' +
            '\n🔘 Помощь' +
            '\n(техническая поддержка и навигация)' +
            '\n\n/pari -> управление пари:' +
            '\n\n🔘 Досрочно завершить пари' +
            '\n(досрочное завершения пари)'
            '\n🔘 Перейти в совместный чат' +
            '\n(кнопка-ссылка в чат с напарником)'
            '\n🔘 Отчеты напарника' +
            '\n(проверка новых отчетов напарника)' +
            '\n🔘 Подтвердить выполнение привычки ' +
            '\n(загрузка отчетов о привычках, ' +
            'формат: фото/видео/кружочки/текст)' +
            '\n\n/profile -> профиль:' +
            '\n\n🔘 Изменить данные о себе' +
            '\n(редактирование профиля)'
            '\n\nПо вопросам работы бота: @kikikita1337')
