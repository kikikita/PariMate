import datetime as dt
from typing import List
from calendar import Calendar
from aiogram import Bot
from core.keyboards.inline import pari_report_from_notify
from core.database.bd import bd_notifications_select, bd_notify_delete


def get_date_notify(day_list: List[str], time: str):
    hours = dt.datetime.strptime(time, '%H:%M').hour
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
    dates = cal.itermonthdates(year, month)
    notification_dates = []
    for i in dates:
        if pari_start <= i <= pari_end and i.weekday() in date_list:
            notification_dates.append(dt.datetime(i.year, i.month, i.day)
                                      + dt.timedelta(hours=hours))
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
                reply_markup=pari_report_from_notify())
    else:
        pass
