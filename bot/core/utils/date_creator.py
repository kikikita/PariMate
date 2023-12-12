import ast
import datetime as dt
from calendar import Calendar


def get_date_notify(day_list: str, time_list: str):
    day_list = ast.literal_eval(day_list)
    time_list = ast.literal_eval(time_list)
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
