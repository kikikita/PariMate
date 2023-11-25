from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.types import Message
from core.keyboards.reply import get_start_kb, main_menu_kb
from aiogram.fsm.context import FSMContext
from core.database.bd import bd_chat_create
from core.filters.chat_type import ChatTypeFilter
import time


router = Router()
router.message.filter(
    ChatTypeFilter(chat_type=["private"])
)


@router.message(Command(commands=["start"]))
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


@router.message(Command(commands=["menu"]))
async def get_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
            'Главное меню',
            reply_markup=main_menu_kb()
            )


@router.message(Command(commands=["help"]))
@router.message(F.text.casefold().in_(['помощь']))
async def get_info(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
            'Проект направлен на мотивацию пользователей' +
            ' к достижению своих целей и развитие полезных' +
            ' привычек через социальное взаимодействие и азарт.',
            reply_markup=main_menu_kb()
            )


@router.message(Command(commands=["chat"]),
                ChatTypeFilter(chat_type=["group", "supergroup"]))
async def get_chat_info(message: Message, bot: Bot):
    chat_members = await bot.get_chat_member(message.chat.id, 6540777845)

    await message.answer(f'{chat_members}')
    chat_link = await bot.create_chat_invite_link(message.chat.id)
    info_msg = await bd_chat_create(message.chat.id, chat_link.invite_link)
    msg = await message.answer(info_msg)
    time.sleep(1)
    await bot.delete_message(message.chat.id, msg.message_id)
    await message.delete()
