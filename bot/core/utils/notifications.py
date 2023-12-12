import datetime as dt
from aiogram import Bot
from core.keyboards.inline import pari_report_from_notify, pari_find_restart
from core.database.bd import (
    bd_notifications_select, bd_notify_delete,  bd_find_time_select,
    bd_find_category_update, bd_last_day_select, bd_report_delete,
    bd_status_clear, bd_chat_delete, bd_get_chat_id, bd_notify_update)
from settings import settings


async def send_notifications(bot: Bot):
    rows = await bd_notifications_select(
        (dt.datetime.now()).replace(minute=0, second=0, microsecond=0)
    )
    await bd_notify_delete()
    if rows:
        data = [dict(row) for row in rows]
        for user_id in data:
            await bot.send_message(
                chat_id=user_id['user_id'],
                text='Привет! Помнишь, ты хотел сформировать ' +
                'новую полезную привычку? Скорее загружай ' +
                'подтверждение. Это важный шаг на пути к успеху!',
                reply_markup=pari_report_from_notify(int(user_id['user_id'])))
    else:
        pass


async def change_category_find(bot: Bot):
    long_time_find, ignore = await bd_find_time_select()
    if long_time_find and ignore:
        data = [dict(row) for row in long_time_find]
        for user in data:
            await bd_find_category_update(user['user_id'])
        ignore_data = [dict(row) for row in ignore]
        for user in ignore_data:
            await bot.send_message(
                user['user_id'],
                '🕑 Твой напарник не дождался ответа... ' +
                'Поиск остановлен',
                reply_markup=pari_find_restart())
            await bd_status_clear(user['user_id'])
    elif long_time_find:
        data = [dict(row) for row in long_time_find]
        for user in data:
            await bd_find_category_update(user['user_id'])
    elif ignore:
        ignore_data = [dict(row) for row in ignore]
        for user in ignore_data:
            await bot.send_message(
                user['user_id'],
                '🕑 Твой напарник не дождался ответа... ' +
                'Поиск остановлен',
                reply_markup=pari_find_restart())
            await bd_status_clear(user['user_id'])
    else:
        return
    return


async def check_ignore_reports(bot: Bot):
    pass


async def last_day_notify(bot: Bot):
    good_result, bad_result = await bd_last_day_select()
    if good_result and bad_result:
        good_data = [dict(row) for row in good_result]
        bad_data = [dict(row) for row in bad_result]
        for user in good_data:
            try:
                await bot.send_message(
                    user['user_id'],
                    f'Привет, {user["name"]} 👋' +
                    '\nПоздравляю тебя с завершением ' +
                    f'{user["habit_week"]}-й недели внедрения привычки! 🎉' +
                    '\nТвой прогресс перенесен на новую неделю, ' +
                    'продолжай в том же духе!'
                    )
                await bd_notify_update(user['user_id'])
            except Exception:
                continue
        for user in bad_data:
            try:
                await bot.send_message(
                    user['user_id'],
                    f'Привет, {user["name"]}!' +
                    '\nК сожалению, на этой неделе ты подтвердил всего ' +
                    f'{user["pari_reports"]} дней выполнения привычки, ' +
                    f'вместо {user["habit_frequency"]} положенных(' +
                    '\nТвое пари завершено, а прогресс сброшен. ' +
                    'Попробуй начать заново!'
                    )
                chat = await bd_get_chat_id(user_id=user['user_id'])
                if chat and user['user_id'] != settings.bots.admin_id:
                    await bot.ban_chat_member(
                        str(chat['chat_id']), user['user_id'])
                await bd_report_delete(user['user_id'])
                await bd_status_clear(user['user_id'])
                await bd_chat_delete(user['user_id'])
            except Exception:
                continue
    elif good_result:
        good_data = [dict(row) for row in good_result]
        for user in good_data:
            try:
                await bot.send_message(
                    user['user_id'],
                    f'Привет, {user["name"]} 👋' +
                    '\nПоздравляю тебя с завершением ' +
                    f'{user["habit_week"]}-й недели внедрения привычки! 🎉' +
                    '\nТвой прогресс перенесен на новую неделю, ' +
                    'продолжай в том же духе!'
                    )
                await bd_notify_update(user['user_id'])
            except Exception:
                continue
    elif bad_result:
        bad_data = [dict(row) for row in bad_result]
        for user in bad_data:
            try:
                await bot.send_message(
                    user['user_id'],
                    f'Привет, {user["name"]}!' +
                    '\nК сожалению, на этой неделе ты подтвердил всего ' +
                    f'{user["pari_reports"]} дней выполнения привычки, ' +
                    f'вместо {user["habit_frequency"]} положенных(' +
                    '\nТвое пари завершено, а прогресс сброшен. ' +
                    'Попробуй начать заново!'
                    )
                chat = await bd_get_chat_id(user_id=user['user_id'])
                if chat and user['user_id'] != settings.bots.admin_id:
                    await bot.ban_chat_member(
                        str(chat['chat_id']), user['user_id'])
                    await bd_report_delete(user['user_id'])
                    await bd_status_clear(user['user_id'])
                    await bd_chat_delete(user['user_id'])
            except Exception:
                continue
    else:
        return
    return
