from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.types import Message
from core.keyboards.inline import get_start_kb, get_main_menu, get_user_link
from aiogram.fsm.context import FSMContext
from core.database.bd import bd_chat_create, bd_get_chat_id
from core.filters.chat_type import ChatTypeFilter
from settings import settings
import time


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


@router.message(Command(commands=["chat"]),
                ChatTypeFilter(chat_type=["group", "supergroup"]))
async def get_chat_update(message: Message, bot: Bot):
    if message.from_user.id == settings.bots.admin_id or\
            message.from_user.id in settings.bots.moder_ids:
        chat_link = await bot.create_chat_invite_link(message.chat.id)
        info_msg = await bd_chat_create(message.chat.id, chat_link.invite_link)
        msg = await message.answer(info_msg)
        time.sleep(1)
        await bot.delete_message(message.chat.id, msg.message_id)
        await message.delete()
    else:
        return


@router.message(Command(commands=["chat_info"]),
                ChatTypeFilter(chat_type=["group", "supergroup"]))
async def get_chat_info(message: Message, bot: Bot):
    if message.from_user.id == settings.bots.admin_id:
        chat_link = await bot.create_chat_invite_link(message.chat.id)
        await message.answer(
            f'Chat_id: {message.chat.id}' +
            f'\nСсылка на чат: {chat_link}')
        await message.delete()
    else:
        return


@router.message(Command(commands=["get_my_id"]))
async def get_my_id(message: Message, bot: Bot):
    await message.answer(f'{message.from_user.id}')


@router.message(F.text.startswith('/unban_'))
async def unban(message: Message, bot: Bot):
    if message.from_user.id == settings.bots.admin_id:
        user_id = message.text.split("_")[1]
        chat_id = message.text.split("_")[2]
        if chat_id is not None:
            if len(chat_id) > 22:
                chat_id = await bd_get_chat_id(chat_id)
            await bot.unban_chat_member(
                    str(chat_id), user_id)
            await message.answer(f'{user_id} разбанен')
        else:
            await message.answer('Не указан chat_id')
        await message.delete()
    else:
        return


@router.message(F.text.startswith('/ban_'))
async def ban(message: Message, bot: Bot):
    if message.from_user.id == settings.bots.admin_id:
        user_id = message.text.split("_")[1]
        chat_id = message.text.split("_")[2]
        if chat_id is not None:
            if len(chat_id) > 22:
                chat_id = await bd_get_chat_id(chat_id)
            await bot.ban_chat_member(
                    str(chat_id), user_id)
            await message.answer(f'{user_id} забанен')
        else:
            await message.answer('Не указан chat_id')
        await message.delete()
    else:
        return


@router.message(F.text.startswith('/get_user_'))
async def funcname(message: Message, bot: Bot):
    if message.from_user.id == settings.bots.admin_id:
        user_id = message.text.split("_")[2]
        await message.answer(text=f'{user_id}',
                             reply_markup=get_user_link(user_id))
    else:
        return
