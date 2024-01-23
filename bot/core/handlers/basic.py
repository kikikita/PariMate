from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from core.keyboards.inline import get_start_kb, get_main_menu
from aiogram.fsm.context import FSMContext
from core.filters.chat_type import ChatTypeFilter


router = Router()


@router.message(Command(commands=["start"]),
                ChatTypeFilter(chat_type=["private"]))
async def get_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
            f'Привет, <b>{message.from_user.first_name}!</b>' +
            '\n\nДобро пожаловать в PariMate! Здесь ты найдешь мотивацию 💪' +
            ' и станешь ближе в достижении своих целей 🏆.'
            '\n\n<i>Как это работает?</i>' +
            '\n1. Подумай, что бы ты хотел изменить в своей жизни? ' +
            '\nВыбери цель, и на ее основе мы подберем тебе напарника, ' +
            'с которым вы заключите пари 🤝' +
            '\n\n2. Просто подтверждай выполнение цели по выбранному тобой ' +
            'расписанию, а также не забывай подтверждать отчеты партнера 🕙' +
            '\n\n3. После 21 дня успешной работы над достижением цели, ' +
            'ты сможешь принять участие в розыгрыше сертификатов Озон 🎉' +
            '\n\nЖелаем не опускать руки на пути к самосовершенствованию!' +
            '\nВсе получится, мы в этом уверены 😊',
            parse_mode=ParseMode.HTML,
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
