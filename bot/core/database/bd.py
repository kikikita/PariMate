import datetime as dt
# import os
import time
from typing import List
from typing import Optional

import asyncpg
from aiogram import Bot
from aiogram.types import ReplyKeyboardRemove
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import dotenv_values

from core.keyboards.inline import pari_choice, pari_find
from core.utils.date_creator import get_date_notify
from settings import settings

config = dotenv_values('.env')

USER = config['POSTGRES_USER']
PSWD = config['POSTGRES_PASSWORD']
DB = config['POSTGRES_DB']
HOST = config['POSTGRES_HOST']
# HOST = os.environ['PG_HOST']


async def bd_interaction(user_id: int, values: list, username: str):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    try:
        await conn.execute(
                        '''
                        INSERT INTO parimate_users(
                            user_id, name, age, sex, username,
                            date_registration)
                        VALUES($1, $2, $3, $4, $5, NOW())''',
                        user_id, values['name'], int(values['age']),
                        values['sex'], username)
    except Exception:
        name = await conn.fetchval(
                        '''
                        UPDATE parimate_users SET name=$2, age=$3, sex=$4
                        WHERE user_id = $1
                        RETURNING parimate_users.name
                        ''', user_id,
                        values['name'], int(values['age']), values['sex'])
        return name
    await conn.close()


async def bd_user_check(user_id: int):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    result = await conn.fetchrow('''
                    SELECT * FROM parimate_users WHERE user_id = $1
                    ''', user_id)
    await conn.close()

    if result is not None:
        pass
    else:
        return False


async def bd_notify_update(user_id: int, notify_day: str | None = None,
                           notify_time: str | None = None):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    user = await bd_user_select(user_id)
    time_list = get_date_notify(
                    user['habit_notification_day'],
                    user['habit_notification_time'])

    await conn.execute('''DELETE FROM parimate_notifications
                          WHERE user_id = $1''', user_id)
    for time_ in time_list:
        await conn.execute('''INSERT INTO parimate_notifications
                            (user_id, date)
                            VALUES($1, $2)
                            ''', user_id, time_)
    if notify_day and notify_time:
        await conn.execute('''UPDATE parimate_users SET
                           habit_notification_day = $2,
                           habit_notification_time = $3
                           WHERE user_id = $1
                           ''', user_id, notify_day, notify_time)
    await conn.close()


async def bd_time_find_update(user_id: int):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    await conn.execute('''
                       UPDATE parimate_users SET time_find_start = NOW()
                       WHERE user_id = $1
                       ''', user_id)
    await conn.close()


async def bd_habit_update(user_id: int, values: list):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    await conn.execute('''
                       UPDATE parimate_users SET habit_category = $2,
                       habit_choice = $3, habit_frequency = $4,
                       habit_mate_sex = $5, time_find_start = $6,
                       habit_notification_day = $7,
                       habit_notification_time = $8
                       WHERE user_id = $1
                       ''', user_id,
                       values['habit_category'], values['habit_choice'],
                       int(values['habit_frequency']),
                       values['habit_mate_sex'], values['time_find_start'],
                       str(values['habit_notification_day']),
                       str(values['habit_notification_time'])
                       )
    await conn.close()


async def bd_user_select(user_id: int | None = None,
                         username: str | None = None):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    if user_id:
        result = await conn.fetchrow('''
                        SELECT * FROM parimate_users WHERE user_id = $1
                        ''', user_id)
    else:
        result = await conn.fetchrow('''
                        SELECT * FROM parimate_users WHERE username = $1
                        ''', username)
    await conn.close()

    if result is not None:
        return dict(result)
    else:
        return False


async def bd_get_pari_mate_id(user_id: int):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    result = await conn.fetchrow('''
                    SELECT pari_mate_id FROM parimate_users WHERE user_id = $1
                    ''', user_id)
    await conn.close()

    if result is not None:
        return dict(result)
    else:
        return False


async def bd_status_clear(user_id: int, pari_end_cause: Optional[str] = None,
                          bot: Optional[Bot] = None):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    result = await conn.fetchrow('''
                    SELECT * FROM parimate_users WHERE user_id = $1
                    ''', user_id)
    pari_mate_id = (dict(result))['pari_mate_id']
    await conn.execute(
                    '''
                    UPDATE parimate_users SET pari_mate_id = NULL,
                    time_find_start = NULL
                    WHERE user_id = $1
                    ''', user_id)
    if pari_end_cause:
        await conn.fetchrow(
                        '''
                        UPDATE parimate_users SET pari_mate_id = NULL,
                        pari_chat_link = NULL, time_find_start = NULL,
                        time_pari_start = NULL, time_pari_end = NULL,
                        pari_reports = Null,
                        pari_end_cause = $2,
                        habit_week = Null
                        WHERE user_id = $1
                        ''', user_id, pari_end_cause)
        await bd_user_notify_delete(user_id)
    if pari_mate_id:
        await conn.execute(
                    '''
                    UPDATE parimate_users SET pari_mate_id = NULL,
                    pari_chat_link = NULL,
                    time_find_start = NOW()
                    WHERE user_id = $1
                    ''', pari_mate_id)
        try:
            await bot.send_message(
                pari_mate_id,
                '😔 Напарник отказался от пари, ' +
                'уже ищем другого..',
                reply_markup=pari_find())
        except Exception:
            pass
    await conn.close()
    return result


async def bd_mate_update(user_id: int, mate_id: int):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    await conn.execute(
                    '''
                    UPDATE parimate_users SET pari_mate_id = $2
                    WHERE user_id = $1
                    ''', user_id, mate_id)
    await conn.execute(
                '''
                UPDATE parimate_users SET pari_mate_id = $2
                WHERE user_id = $1
                ''', mate_id, user_id)
    await conn.close()


async def bd_chat_delete(user_id: int, bot: Bot | None = None):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    result = await conn.fetchrow('''
                    SELECT * FROM parimate_chats WHERE user_1 = $1
                    OR user_2 = $1
                    LIMIT 1
                    ''', user_id)
    until_date = dt.datetime.now() + dt.timedelta(minutes=2)
    if result:
        for user_id in (result['user_1'], result['user_2']):
            if user_id and user_id != 1:
                try:
                    await bot.ban_chat_member(
                        result['chat_id'],
                        user_id,
                        until_date=until_date)
                except Exception:
                    pass
    await conn.execute('''
                        UPDATE parimate_chats SET
                        user_1 = Null, user_2 = Null
                        WHERE user_1 = $1 OR user_2 = $1
                        ''', user_id)
    await conn.close()


async def send_mate_msg(user: dict,
                        mate: dict,
                        bot: Bot,
                        ):
    try:
        await bot.send_message(
            user["user_id"],
            'Партнер по привычке найден:' +
            f'\n{mate["name"]}, {mate["age"]}' +
            f'\nЦель: {mate["habit_choice"].lower()} ' +
            f'{mate["habit_frequency"]} раз(-а) в неделю.',
            reply_markup=pari_choice())
    except Exception:
        pass
    return


async def match(conn):
    users_without_partner_records = await conn.fetch(
        '''
        SELECT * FROM parimate_users
        WHERE pari_mate_id IS NULL
        AND time_find_start IS NOT NULL
        ORDER BY habit_mate_sex, time_find_start
        ''')
    # search_time = dt.datetime.now()
    partners = {}
    users_without_partner = [
        dict(row) for row in users_without_partner_records]
    for user in users_without_partner:
        if user['user_id'] not in partners:
            filtered_users = list(
                filter(
                    lambda u_d: u_d['user_id'] != user['user_id'] and
                    u_d['user_id'] not in partners and
                    (u_d['habit_mate_sex'] == user['sex'] or
                     u_d['habit_mate_sex'] == 'Не имеет значения') and
                    u_d['habit_category'] == user['habit_category'],
                    users_without_partner))
            if user['habit_mate_sex'] != 'Не имеет значения':
                filtered_users = list(
                    filter(lambda u_d: u_d['sex'] == user['habit_mate_sex'],
                           filtered_users)
                )
            filtered_users.sort(key=lambda x:
                                (x['habit_choice'] != user['habit_choice'],
                                 x['time_find_start']))
            user_partner = None
            if len(filtered_users) > 0:
                user_partner = filtered_users[0]
            if user_partner is not None:
                partners[user['user_id']] = user_partner['user_id']
                partners[user_partner['user_id']] = user['user_id']
    return partners, users_without_partner


async def match_partners(bot: Bot):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    partners, users = await match(conn)
    async with conn.transaction():
        for user_id in partners:
            mate_id = partners[user_id]
            user = list(filter(lambda x: x["user_id"] == user_id, users))[0]
            mate = list(filter(lambda x: x["user_id"] == mate_id, users))[0]

            await conn.execute('''
                    UPDATE parimate_users SET
                    pari_mate_id = $2,
                    time_find_start = NOW()
                    WHERE user_id = $1
                ''', user_id, mate_id)
            await send_mate_msg(user, mate, bot)
    await conn.close()


async def bd_chat_create(chat_id: int, chat_link: str):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    result = await conn.fetchrow('''
                    SELECT * FROM parimate_chats
                    WHERE chat_id = $1
                    ''', chat_id)
    if result is not None:
        await conn.execute('''UPDATE parimate_chats SET chat_link = $2
                           WHERE chat_id = $1''', chat_id, chat_link)
        msg = 'Чат существует. Ссылка обновлена'
    else:
        await conn.execute('''INSERT INTO parimate_chats(chat_id, chat_link)
                           VALUES($1, $2)''', chat_id, chat_link)
        msg = 'Чат создан'
    await conn.close()
    return msg


async def bd_chat_select(user_id: int):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    result = await conn.fetchrow('''
                    SELECT * FROM parimate_chats
                    WHERE user_1 = $1 or user_2 = $1
                    ''', user_id)
    await conn.close()

    if result is not None:
        return dict(result)
    else:
        return False


async def bd_chat_update(user_id: int, bot: Bot, scheduler: AsyncIOScheduler):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    mate_id = (await bd_user_select(user_id))['pari_mate_id']
    result = await conn.fetchrow(
        '''
        WITH t2 AS (SELECT *,
        CASE
            WHEN user_1 in ($1) and user_2 is Null
                THEN 0
            WHEN user_1 in ($1, $2) and user_2 in ($1, $2)
                THEN 1
            WHEN user_1 in ($1, $2)
                THEN 2
            WHEN user_1 is Null
                THEN 3
            ELSE 4
        END AS user_check
        FROM parimate_chats
        ORDER BY user_check
        LIMIT 1)

        UPDATE parimate_chats t1
        SET user_1 =
        CASE
            WHEN t2.user_check = 3 THEN $1
            ELSE t2.user_1
        END,
        user_2 =
        CASE
            WHEN t2.user_check = 3 THEN 1
            WHEN t2.user_check = 2 AND t2.user_1 != $1 THEN $1
            ELSE t2.user_2
        END
        FROM t2
        WHERE t1.chat_id = t2.chat_id AND user_check != 4
        RETURNING t1.*
        ''', user_id, mate_id)

    if result is not None:
        if result['user_1'] == mate_id and result['user_2'] == user_id:
            for user_id in (result['user_1'], result['user_2']):
                try:
                    await bot.send_message(
                        user_id,
                        'Напарник подтвердил пари!'
                        '\n\nВот ссылка на совместный чат:' +
                        f'{result["chat_link"]}' +
                        '\n\nЖми /help, чтобы ознакомиться ' +
                        'с функционалом бота',
                        reply_markup=ReplyKeyboardRemove()
                    )
                except Exception:
                    continue
                await bd_date_waiting_update(user_id)

            time_start = dt.datetime.now()
            time_end = (dt.datetime.now() + dt.timedelta(days=7))

            await conn.execute(
                '''
                UPDATE parimate_users SET pari_chat_link = $3,
                time_pari_start = $4, time_pari_end = $5,
                time_find_start = Null
                WHERE user_id IN ($1, $2)
                ''', result['user_1'], result['user_2'],
                result["chat_link"], time_start,
                time_end)
            await conn.close()
    else:
        scheduler.add_job(
            bd_chat_update, 'date',
            run_date=(dt.datetime.now() + dt.timedelta(seconds=5)),
            kwargs={'user_id': user_id,
                    'bot': bot,
                    'scheduler': scheduler})
        await bot.send_message(settings.bots.tech_id,
                               text='Нет чатов для пользователей')
    await conn.close()
    return result


async def bd_pari_report_create(user_id: int, pari_report: List[str],
                                report_time):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    await conn.execute('''
                       INSERT INTO parimate_reports
                       (user_id, pari_report, date, status, date_waiting)
                       VALUES($1, $2, $3, $4, $5)
                       ''', user_id, pari_report, report_time,
                       'waiting', report_time)
    await conn.close()


async def bd_pari_report_get(user_id: int, status: str):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    result = await conn.fetchrow('''
                    SELECT * FROM parimate_reports
                    WHERE user_id = $1 and status = $2
                    ''', user_id, status)
    await conn.close()

    if result is not None:
        return result
    else:
        return False


async def bd_pari_report_update(report_id: int, status: str,
                                reason: str | None = None):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    await conn.execute(
                    '''
                    UPDATE parimate_reports SET status = $2, reason = $3
                    WHERE report_id = $1
                    ''', report_id, status, reason)
    await conn.close()


async def bd_user_report_update(user_id: int):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    await conn.execute(
                    '''
                    UPDATE parimate_users SET
                    pari_reports = COALESCE(pari_reports, 0) + 1
                    WHERE user_id = $1
                    ''', user_id)
    await conn.close()


async def bd_notify_delete():
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)

    await conn.execute('''DELETE FROM parimate_notifications
                        WHERE date < NOW() - INTERVAL '2' HOUR''')
    await conn.close()


async def bd_user_notify_delete(user_id: int):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)

    await conn.execute('''DELETE FROM parimate_notifications
                        WHERE user_id = $1''', user_id)
    await conn.close()


async def bd_notifications_select(time):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    rows = await conn.fetch('''
                    SELECT user_id FROM parimate_notifications
                    WHERE date = $1 and status is Null
                    ''', time)

    await conn.close()
    return rows


async def bd_find_time_select():
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    long_time_find = await conn.fetch('''
                    SELECT * FROM parimate_users
                    WHERE ((time_find_start is not NULL)
                    AND (time_find_start < NOW() - INTERVAL '30' MINUTE)
                    AND (time_pari_start is NULL))
                    AND pari_mate_id is NULL
                    ''')
    ignoring = await conn.fetch('''
                    SELECT user_id
                    FROM parimate_users
                    WHERE ((time_find_start is not NULL)
                    AND (time_find_start < NOW() - INTERVAL '30' MINUTE)
                    AND (time_pari_start is NULL))
                    AND pari_mate_id is NOT NULL
                    AND user_id not in (
                    SELECT user_1 FROM parimate_chats WHERE user_1 IS NOT NULL)
                    ''')
    await conn.close()
    return long_time_find, ignoring


async def bd_find_category_update(user_id: int):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    await conn.execute('''
                    UPDATE parimate_users SET
                    habit_category = 'all'
                    WHERE user_id = $1
                    ''', user_id)

    await conn.close()


async def bd_get_chat_id(chat_link: str | None = None,
                         user_id: str | None = None,
                         second: bool | None = None):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    if chat_link:
        result = await conn.fetchrow('''
                        SELECT chat_id FROM parimate_chats
                        WHERE chat_link = $1
                        ''', chat_link)
    elif user_id:
        if second:
            result = await conn.fetchrow('''
                        SELECT chat_id FROM parimate_chats
                        WHERE user_2 = $1
                        ''', user_id)
        else:
            result = await conn.fetchrow('''
                            SELECT chat_id FROM parimate_chats
                            WHERE user_1 = $1 or user_2 = $1
                            ''', user_id)
    else:
        await conn.close()
        return
    await conn.close()
    return result


async def bd_report_delete(user_id: int):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    await conn.execute('''
                    UPDATE parimate_reports SET
                    status = 'deleted'
                    WHERE user_id = $1
                    ''', user_id)

    await conn.close()


async def bd_date_waiting_update(user_id: int):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    user = await bd_user_select(user_id)
    if user['pari_mate_id']:
        await conn.execute('''
                    UPDATE parimate_reports SET
                    date_waiting = NOW()
                    WHERE user_id = $1 AND
                    status = 'waiting'
                    ''', user['pari_mate_id'])

    await conn.execute('''
                    UPDATE parimate_reports SET
                    date_waiting = NOW()
                    WHERE user_id = $1 AND
                    status = 'waiting'
                    ''', user_id)

    await conn.close()


async def bd_report_ignore():
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    ignore_1_day = await conn.fetch(
                    '''
                    SELECT DISTINCT pr.user_id, pu.pari_mate_id
                    FROM parimate_reports pr
                    JOIN parimate_users pu ON pr.user_id = pu.user_id
                    JOIN parimate_chats pc ON (pc.user_1 = pr.user_id
                    OR pc.user_2 = pr.user_id)
                    WHERE pr.status = 'waiting'
                    AND (pr.date_waiting < NOW() - INTERVAL '1' DAY)
                    AND pu.pari_mate_id IS NOT NULL
                    AND (EXISTS (
                            SELECT 1 FROM parimate_chats
                            WHERE user_1 = pu.pari_mate_id)
                        OR EXISTS (
                            SELECT 1 FROM parimate_chats
                            WHERE user_2 = pu.pari_mate_id)
                        )
                    AND NOT EXISTS (
                        SELECT 1
                        FROM parimate_reports pr
                        WHERE pr.user_id = pu.user_id
                        AND pr.date_waiting < NOW() - INTERVAL '2' DAY
                    )
                    ''')

    ignore_2_day = await conn.fetch(
                    '''
                    SELECT DISTINCT pr.user_id, pu.pari_mate_id
                    FROM parimate_reports pr
                    JOIN parimate_users pu ON pr.user_id = pu.user_id
                    JOIN parimate_chats pc ON (pc.user_1 = pr.user_id
                    OR pc.user_2 = pr.user_id)
                    WHERE pr.status = 'waiting'
                    AND (pr.date_waiting < NOW() - INTERVAL '2' DAY)
                    AND pu.pari_mate_id IS NOT NULL
                    AND (EXISTS (
                            SELECT 1 FROM parimate_chats
                            WHERE user_1 = pu.pari_mate_id)
                        OR EXISTS (
                            SELECT 1 FROM parimate_chats
                            WHERE user_2 = pu.pari_mate_id)
                        )
                    ''')
    await conn.close()
    return ignore_1_day, ignore_2_day


async def bd_last_day_select():
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    bad_result = await conn.fetch('''
                    SELECT * FROM parimate_users
                    WHERE time_pari_end <= NOW()
                    AND COALESCE(pari_reports, 0) < (habit_frequency/2)
                    ''')
    time.sleep(0.5)
    good_result = await conn.fetch('''
                    UPDATE parimate_users SET
                    habit_week = COALESCE(habit_week, 0) + 1,
                    time_pari_end = time_pari_end + INTERVAL '7 days',
                    pari_reports = 0
                    WHERE time_pari_end <= NOW()
                    AND COALESCE(pari_reports, 0) >= (habit_frequency/2)
                    RETURNING *
                    ''')
    await conn.close()
    return good_result, bad_result


async def bd_habit_clear(user_id: int):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    await conn.execute('''
                    UPDATE parimate_users SET habit_category = Null,
                    habit_choice = Null, habit_frequency = Null,
                    habit_mate_sex = Null, time_find_start = Null,
                    habit_notification_day = Null,
                    habit_notification_time = Null
                    WHERE user_id = $1
                    ''', user_id)

    await conn.close()


# ################ ADMIN QUERIES ###################
async def bd_get_statistics():
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    statistics = {}
    statistics['in_pari'] = await conn.fetchval(
                    '''
                    SELECT COUNT(user_id) as CNT FROM parimate_users
                    WHERE time_pari_start is not NULL
                    ''')
    statistics['in_find'] = await conn.fetchval('''
                    SELECT COUNT(user_id) as CNT FROM parimate_users
                    WHERE time_find_start is not NULL
                    ''')
    statistics['empty_chats'] = await conn.fetchval('''
                    SELECT COUNT(chat_id) as CNT FROM parimate_chats
                    WHERE user_1 is NULL
                    ''')
    statistics['users_1_week'] = await conn.fetchval('''
                    SELECT COUNT(user_id) AS CNT FROM parimate_users
                    WHERE habit_week = 1
                    ''')
    statistics['users_2_week'] = await conn.fetchval('''
                    SELECT COUNT(user_id) AS CNT FROM parimate_users
                    WHERE habit_week = 2
                    ''')
    statistics['users_3_week'] = await conn.fetchval('''
                    SELECT COUNT(user_id) AS CNT FROM parimate_users
                    WHERE habit_week >= 3
                    ''')
    await conn.close()
    return statistics
