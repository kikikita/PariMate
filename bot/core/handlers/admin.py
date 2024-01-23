import datetime as dt
from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.types import Message
from core.filters.chat_type import ChatTypeFilter
from core.keyboards.inline import get_user_link
from core.database.bd import (
    bd_chat_create, bd_get_chat_id, bd_user_select,
    bd_status_clear, bd_chat_delete, bd_get_statistics)
from settings import settings
import time


router = Router()


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


@router.message(F.text.startswith('/get_user_'))
async def funcname(message: Message, bot: Bot):
    if message.from_user.id == settings.bots.admin_id or\
            message.from_user.id in settings.bots.moder_ids:
        try:
            user_id = int(message.text.split("_")[2])
            user = await bd_user_select(user_id)
        except Exception:
            username = message.text.split("_")[2]
            user = await bd_user_select(username=username)
        if user:
            await message.answer(
                text=f'ID: {user["user_id"]} \nUsername: @{user["username"]}' +
                f'\nИмя: {user["name"]}' +
                f'\nВозраст: {user["age"]}, Пол: {user["sex"]}' +
                f'\nПривычка: {user["habit_choice"]}' +
                f'\nРегулярность: {user["habit_frequency"]} дней' +
                f'\nПол партнера: {user["habit_mate_sex"]}',
                reply_markup=get_user_link(user["user_id"]))
        else:
            await message.answer('Пользователь не найден')
    else:
        return


@router.message(F.text.startswith('/update_chat_'))
async def update_chat(message: Message, bot: Bot):
    if message.from_user.id == settings.bots.admin_id or\
            message.from_user.id in settings.bots.moder_ids:
        user_id = int(message.text.split("_")[2])
        pari_mate_id = (await bd_user_select(user_id))['pari_mate_id']
        chat = await bd_get_chat_id(user_id=pari_mate_id, second=True)
        try:
            until_date = dt.datetime.now() + dt.timedelta(minutes=2)
            await bot.ban_chat_member(
                    str(chat['chat_id']), user_id, until_date=until_date)
            await message.answer('Забанен из старого чата')
        except Exception:
            pass
        for user in (user_id, pari_mate_id):
            try:
                await bot.send_message(
                    user,
                    'Ваш чат с напарником обновлен, ' +
                    'проверь, находишься ли ты в нем?' +
                    '\nДля этого нажми /pari -> "Перейти в совместный чат"')
            except Exception:
                pass
        await message.answer('Успешно')
    else:
        return


@router.message(F.text.startswith('/send_message_'))
async def sen_message_chat(message: Message, bot: Bot):
    if message.from_user.id == settings.bots.admin_id or\
            message.from_user.id in settings.bots.moder_ids:
        user_id = int(message.text.split("_")[2])
        text = message.text.split("_")[3]
        try:
            await bot.send_message(user_id, text)
            await message.answer('Сообщение отправлено')
        except Exception:
            pass
    else:
        return


@router.message(F.text.startswith('/ban_chat_'))
async def ban_chat(message: Message, bot: Bot):
    if message.from_user.id == settings.bots.admin_id:
        chat_id = (message.text.split("_")[2])
        user_id = int(message.text.split("_")[3])
        until_date = dt.datetime.now() + dt.timedelta(minutes=2)
        await bot.ban_chat_member(
                chat_id,
                user_id, until_date=until_date)
        await message.answer('Забанен')
    else:
        return


@router.message(F.text.startswith('/ban_'))
async def ban(message: Message, bot: Bot):
    if message.from_user.id == settings.bots.admin_id:
        user_id = int(message.text.split("_")[1])
        chat_id = message.text.split("_")[2]
        if chat_id is not None:
            if len(chat_id) > 22:
                chat_id = await bd_get_chat_id(chat_id)
            await bot.ban_chat_member(
                    str(chat_id), user_id)
            await message.answer(f'{user_id} забанен')
        else:
            user = await bd_user_select(user_id)
            if user['time_pari_start']:
                await bd_chat_delete(user_id)
            await bd_status_clear(user_id)
            await message.answer(f'{user_id} забанен')
        await message.delete()
    else:
        return


@router.message(F.text.startswith('/statistics'))
async def statistics(message: Message, bot: Bot):
    if message.from_user.id == settings.bots.admin_id or\
            message.from_user.id in settings.bots.moder_ids:
        stats = await bd_get_statistics()
        time = dt.datetime.now().strftime("%d-%m-%y %H:%M")
        await message.answer(
            f'Статистика PariMate на {time}' +
            f'\n\nУчаствуют в пари: {stats["in_pari"]}' +
            f'\nНаходятся в поиске: {stats["in_find"]}' +
            f'\nСвободно чатов: {stats["empty_chats"]}' +
            f'\n\nЛюдей на 1й неделе: {stats["users_1_week"]}' +
            f'\nЛюдей на 2й неделе: {stats["users_2_week"]}' +
            f'\nЛюдей на 3й+ неделе: {stats["users_3_week"]}'
            )
    else:
        return
