from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from core.keyboards.inline import pari_find_start, pari_find
from core.database.bd import (
    bd_time_find_update, bd_status_clear, bd_notify_update,
    bd_chat_update, bd_user_select, bd_chat_delete)
from core.filters.chat_type import ChatTypeFilter


router = Router()
router.message.filter(
    ChatTypeFilter(chat_type=["private"])
)


# find_cancel #find_accept #find_decline
@router.callback_query(F.data.startswith("find_start"))
async def find_start(callback: CallbackQuery):
    await callback.message.edit_text(
        '⏳ Подбираем партнера по привычке...' +
        '\n✉ Сообщим, как будет готово',
        reply_markup=pari_find())
    await bd_time_find_update(callback.from_user.id)
    await callback.answer()


# find_cancel
@router.callback_query(F.data.startswith("find_cancel"))
async def find_cancel(callback: CallbackQuery, bot: Bot):
    try:
        action = callback.data.split("_")[2]
    except Exception:
        pass
    user = await bd_user_select(callback.from_user.id)
    if user['pari_mate_id'] and action != 'reject':
        await callback.message.edit_text(
            'Мы нашли для тебя партнера по привычке' +
            '\nПроверь, сообщение ниже 👇')
        return
    else:
        if user['time_pari_start']:
            if user['pari_mate_id']:
                await callback.message.edit_text(
                    'Пари уже началось')
            else:
                await callback.message.edit_text(
                    'Поиск отменен, пари продолжится без напарника' +
                    '\n🤖 Твои отчеты будет подтверждать PariMate')
                await bd_status_clear(callback.from_user.id, bot=bot)
            return
        days_string = (str(user["habit_notification_day"])[1:-1]
                       .replace("'", ""))
        time_string = (str(user["habit_notification_time"])[1:-1]
                       .replace("'", ""))
        await callback.message.edit_text('Поиск отменен')
        await callback.message.answer(
            f'Твои настройки привычки:'
            f'\n\n🎯 Цель: {user["habit_choice"]}' +
            f'\n📅 Регулярность: {days_string}' +
            f'\n🔔 Время напоминаний: {time_string}' +
            f'\n🚻 Пол партнера: {user["habit_mate_sex"]}',
            reply_markup=pari_find_start()
        )
        await bd_status_clear(callback.from_user.id, bot=bot)
        # if result['time_pari_start'] is None:
        await bd_chat_delete(callback.from_user.id, bot=bot)


@router.callback_query(F.data.startswith("find_accept"))
async def find_accept(callback: CallbackQuery, bot: Bot,
                      scheduler: AsyncIOScheduler):
    await callback.message.edit_text('Ожидаем подтверждение от напарника')
    await bd_notify_update(callback.from_user.id)
    await bd_chat_update(callback.from_user.id, bot, scheduler)
