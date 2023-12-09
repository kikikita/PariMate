import datetime as dt
from typing import List
from calendar import Calendar
from aiogram import Bot
from core.keyboards.inline import pari_report_from_notify
from core.database.bd import (
    bd_notifications_select, bd_notify_delete,  bd_find_time_select,
    bd_find_category_update, bd_last_day_select, bd_report_delete,
    bd_status_clear, bd_chat_delete, bd_get_chat_id)
from settings import settings


def get_date_notify(day_list: List[str], time_list: List[str]):
    hours_list = []
    for hour in time_list:
        hours_list.append(dt.datetime.strptime(hour, '%H:%M').hour)
    date_list = []
    for day in day_list:
        if day == 'Пн':
            date_list.append(0)
        elif day == 'Вт':
            date_list.append(1)
        elif day == 'Ср':
            date_list.append(2)
        elif day == 'Чт':
            date_list.append(3)
        elif day == 'Пт':
            date_list.append(4)
        elif day == 'Сб':
            date_list.append(5)
        elif day == 'Вс':
            date_list.append(6)
        else:
            continue
    cal = Calendar()
    year = dt.datetime.now().year
    month = dt.datetime.now().month
    pari_start = dt.datetime.now().date()
    pari_end = (dt.datetime.now() + dt.timedelta(days=7)).date()
    cur_month = [i for i in cal.itermonthdates(year, month)]

    next_mont = [i for i in cal.itermonthdates(year+1 if month == 12 else year,
                                               month+1 if month != 12 else 1)]

    set_back = set(cur_month)
    set_forward = set(next_mont)
    set_back.difference_update(set_forward)

    dates = (list(set_back) + list(set_forward))

    notification_dates = []
    for i in dates:
        if pari_start <= i <= pari_end and i.weekday() in date_list:
            for hour in hours_list:
                notification_dates.append(dt.datetime(i.year, i.month, i.day)
                                          + dt.timedelta(hours=hour))
    return notification_dates


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
    rows = await bd_find_time_select()
    if rows:
        data = [dict(row) for row in rows]
        for user_id in data:
            await bd_find_category_update(user_id['user_id'])
        for user in data:
            await bot.send_message(
                settings.bots.tech_id,
                f'Пользователь {user["user_id"]} в поиске > 30 мин' +
                '\nКатегория изменена на "all"'
                f'\n\nИнфо: /get_user_{user["user_id"]}')
    return


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
