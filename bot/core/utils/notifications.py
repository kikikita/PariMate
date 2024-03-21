import datetime as dt
from aiogram import Bot
from core.keyboards.inline import (
    pari_report_from_notify, pari_find_restart, tech_report)
from core.database.bd import (
    bd_notifications_select, bd_notify_delete,  bd_find_time_select,
    bd_find_category_update, bd_last_day_select, bd_report_delete,
    bd_status_clear, bd_chat_delete, bd_notify_update,
    bd_report_ignore, bd_get_statistics)
from settings import settings


async def send_statistics(bot: Bot):
    stats = await bd_get_statistics()
    time = dt.datetime.now().strftime("%d-%m-%y %H:%M")
    try:
        await bot.send_message(
            settings.bots.tech_id,
            f'Статистика PariMate на {time}' +
            f'\n\nУчаствуют в пари: {stats["in_pari"]}' +
            f'\nНаходятся в поиске: {stats["in_find"]}' +
            f'\nСвободно чатов: {stats["empty_chats"]}' +
            f'\n\nЛюдей на 1й неделе: {stats["users_1_week"]}' +
            f'\nЛюдей на 2й неделе: {stats["users_2_week"]}' +
            f'\nЛюдей на 3й+ неделе: {stats["users_3_week"]}'
            )
    except Exception:
        return


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
            await bd_status_clear(user['user_id'],
                                  pari_end_cause='long_time_accept')
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
            await bd_status_clear(user['user_id'],
                                  pari_end_cause='long_time_accept')
    else:
        return
    return


async def check_ignore_reports(bot: Bot):
    ignore_1_day, ignore_2_day = await bd_report_ignore()
    good_data = [dict(row) for row in ignore_1_day]
    bad_data = [dict(row) for row in ignore_2_day]

    for user in good_data:
        try:
            message = ('Хэй! Твой напарник ждет подтверждения ' +
                       'своего отчета больше суток!' +
                       '\nЕще день, и нам придется исключить тебя из пари(')
            await bot.send_message(user['pari_mate_id'], message,
                                   reply_markup=tech_report(user['user_id']))
        except Exception:
            continue

    for user in bad_data:
        try:
            message = ('Привет! Ты не подверждал отчеты '
                       'своего напарника больше двух дней.'
                       '\nПо этой причине нам пришлось исключить тебя '
                       'из пари и сбросить твой прогресс(')
            await bot.send_message(user['pari_mate_id'], message)
            try:
                await bot.send_message(
                    user['user_id'],
                    '❗ К сожалению, ваш напарник не подтверждал ваши отчеты,' +
                    ' и нам пришлось исключить его из пари.' +
                    '\nПродолжайте отправлять ' +
                    'подтверждения своих привычек через '
                    'интерфейс бота, а мы заменим вашего напарника!')
            except Exception:
                pass
            try:
                await bot.send_message(
                    settings.bots.tech_id,
                    f"Пользователь {user['user_id']} остался " +
                    "без напарника!\nПроверьте его отчеты о привычках",
                    reply_markup=tech_report(user['user_id']))
            except Exception:
                pass
            await bd_report_delete(user['pari_mate_id'])
            await bd_status_clear(user['pari_mate_id'],
                                  pari_end_cause='report_ignore')
            await bd_chat_delete(user['pari_mate_id'], bot=bot)
        except Exception:
            continue

    return


async def last_day_notify(bot: Bot):
    good_result, bad_result = await bd_last_day_select()
    if good_result:
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
                if user["habit_week"] == 3:
                    await bot.send_message(
                        user['user_id'],
                        '🎁 Достижение 3-й недели означает, ' +
                        'что теперь ты можешь принять участие' +
                        'в розыгрыше сертификатов Ozon!' +
                        '\n\nДля этого, пройди опрос по ссылке,'
                        'в конце опроса укажи свой tg-профиль. ' +
                        'Желаю удачи!' +
                        '\n\nhttps://forms.gle/omTKXF9S2humZqPa6')
                await bd_notify_update(user['user_id'])
            except Exception:
                continue
    if bad_result:
        bad_data = [dict(row) for row in bad_result]
        for user in bad_data:
            try:
                await bot.send_message(
                    user['user_id'],
                    f'Привет, {user["name"]}!' +
                    '\nК сожалению, на этой неделе ты подтвердил всего ' +
                    f'{user["pari_reports"] if user["pari_reports"] else 0} ' +
                    'дней выполнения привычки, ' +
                    f'вместо {user["habit_frequency"]} положенных(' +
                    '\nТвое пари завершено, а прогресс сброшен. ' +
                    'Попробуй начать заново!'
                )
                if user['pari_mate_id']:
                    try:
                        await bot.send_message(
                            user['pari_mate_id'],
                            '❗ К сожалению, нам пришлось исключить вашего ' +
                            'напарника из пари, по причине недостаточного ' +
                            'кол-ва подтверждений. Совместный чат удален.' +
                            '\nПродолжайте отправлять ' +
                            'подтверждения своих привычек через '
                            'интерфейс бота, а мы заменим вашего напарника!')
                    except Exception:
                        pass
                    try:
                        await bot.send_message(
                            settings.bots.tech_id,
                            f"Пользователь {user['pari_mate_id']} остался " +
                            'без напарника!\nПроверьте его отчеты о привычках',
                            reply_markup=tech_report(user['user_id'])
                        )
                    except Exception:
                        pass
                    await bd_report_delete(user['user_id'])
                    await bd_status_clear(user['user_id'],
                                          pari_end_cause='not_enough_reports')
                    await bd_chat_delete(user['user_id'], bot=bot)
            except Exception:
                continue
