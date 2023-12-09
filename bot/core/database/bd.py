from typing import List
import asyncpg
from typing import Optional
from aiogram import Bot
from aiogram.types import Message, ReplyKeyboardRemove
from dotenv import dotenv_values
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from core.keyboards.reply import pari_choice, pari_find
from aiogram.fsm.context import FSMContext
from apscheduler.jobstores.base import JobLookupError
from core.utils.states import Habit
from settings import settings
import datetime as dt
import time
# import os


config = dotenv_values('.env')

USER = config['POSTGRES_USER']
PSWD = config['POSTGRES_PASSWORD']
DB = config['POSTGRES_DB']
HOST = config['POSTGRES_HOST']
# HOST = os.environ['PG_HOST']


async def bd_interaction(user_id: int, values: list):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    try:
        await conn.execute(
                        '''
                        INSERT INTO parimate_users(user_id, name, age, sex)
                        VALUES($1, $2, $3, $4)''',
                        user_id, values['name'], int(values['age']),
                        values['sex'])
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


async def bd_notify_update(user_id: int, time_list,
                           notify_day: str | None = None,
                           notify_time: str | None = None):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    result = await conn.fetch('''
                    SELECT * FROM parimate_notifications WHERE user_id = $1
                    ''', user_id)
    if result:
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


async def bd_user_select(user_id: int):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    result = await conn.fetchrow('''
                    SELECT * FROM parimate_users WHERE user_id = $1
                    ''', user_id)
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


async def bd_status_clear(user_id: int, pari_end_cause: Optional[str] = None):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    result = await conn.fetchrow('''
                    SELECT * FROM parimate_users WHERE user_id = $1
                    ''', user_id)
    pari_mate_id = (dict(result))['pari_mate_id']
    await conn.fetchrow(
                    '''
                    UPDATE parimate_users SET pari_mate_id = NULL,
                    pari_chat_link = NULL, time_find_start = NULL,
                    time_pari_start = NULL, time_pari_end = NULL,
                    pari_reports = Null,
                    pari_end_cause = $2
                    WHERE user_id = $1
                    ''', user_id, pari_end_cause)
    if pari_mate_id:
        await conn.execute(
                    '''
                    UPDATE parimate_users SET pari_mate_id = NULL,
                    time_find_start = NOW()
                    WHERE user_id = $1
                    ''', pari_mate_id)
    await bd_user_notify_delete(user_id)
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
    if result is not None:
        if result['user_1'] == user_id and result['user_2'] is not None\
                and result['user_2'] != 1:
            await conn.execute(
                        '''
                        UPDATE parimate_chats SET
                        ban_list = user_1, user_1 = user_2, user_2 = 1
                        WHERE user_1 = $1
                        ''', user_id)
        elif result['user_1'] == user_id and result['user_2'] is not None\
                and result['user_2'] == 1:
            if bot and result['ban_list'] is not None:
                await bot.unban_chat_member(result['chat_id'],
                                            result['user_id'])
            await conn.execute(
                        '''
                        UPDATE parimate_chats SET
                        user_1 = Null, user_2 = Null,
                        time_start = Null, time_end = Null,
                        ban_list = Null
                        WHERE user_1 = $1
                        ''', user_id)
        elif result['user_1'] == user_id\
                and (result['user_2'] is None or result['user_2'] == 1):
            if bot and result['ban_list'] is not None:
                await bot.unban_chat_member(result['chat_id'],
                                            result['user_id'])
            await conn.execute(
                        '''
                        UPDATE parimate_chats SET
                        user_1 = Null,
                        time_start = Null, time_end = Null,
                        ban_list = Null
                        WHERE user_1 = $1
                        ''', user_id)
        elif result['user_2'] == user_id:
            await conn.execute(
                        '''
                        UPDATE parimate_chats SET ban_list = user_2,
                        user_2 = 1
                        WHERE user_2 = $1
                        ''', user_id)
    return


async def bd_check_cancel(message: Message, scheduler: AsyncIOScheduler):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    result = await conn.fetchrow('''
                    SELECT pari_mate_id FROM parimate_users WHERE user_id = $1
                    ''', message.from_user.id)
    if result['pari_mate_id'] is not None:
        return

    else:
        await message.answer('Напарник отказался от участия в пари, ' +
                             'уже ищем другого...',
                             reply_markup=pari_find())
        scheduler.resume_job(f'mate_find_{message.from_user.id}')
        try:
            scheduler.remove_job(f'mate_cancel_{message.from_user.id}')
            scheduler.remove_job(f'chat_find_{message.from_user.id}')
        except JobLookupError:
            return


async def send_mate_msg(user: dict,
                        mate: dict,
                        state: FSMContext,
                        bot: Bot,
                        ):
    await state.set_state(Habit.mate_find)
    await bot.send_message(
        user["user_id"],
        'Партнер по привычке найден:' +
        f'\n{mate["name"]}, {mate["age"]}' +
        f'\nЦель: {mate["habit_choice"].lower()} ' +
        f'{mate["habit_frequency"]} раз(-а) в неделю.',
        reply_markup=pari_choice())
    try:
        await bot.send_message(
            mate["user_id"],
            'Партнер по привычке найден:' +
            f'\n{user["name"]}, {user["age"]}' +
            f'\nЦель: {user["habit_choice"].lower()} ' +
            f'{user["habit_frequency"]} раз(-а) в неделю.',
            reply_markup=pari_choice())
    except Exception:
        pass
    return


async def bd_mate_find(message: Message,
                       scheduler: AsyncIOScheduler, state: FSMContext,
                       bot: Bot):
    values = await bd_user_select(message.from_user.id)
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    if values['habit_mate_sex'] == 'Не имеет значения':
        result = await conn.fetchrow(
                        '''
                        SELECT * FROM parimate_users
                        WHERE user_id != $1 and habit_category = $2
                        and (habit_mate_sex = $3 or
                        habit_mate_sex = 'Не имеет значения')
                        and (pari_mate_id IS NULL or pari_mate_id = $1)
                        and time_find_start IS NOT NULL
                        ORDER BY time_find_start
                        Limit 1
                        ''', message.from_user.id,
                        values['habit_category'],
                        values['sex'])
        await conn.close()
        if result is None or values['time_find_start'] is None:
            return
        else:
            mate_find = scheduler.get_job(f'send_mate_msg_{result["user_id"]}')
            if result['time_find_start'] > values['time_find_start']:
                await bd_mate_update(message.from_user.id, result['user_id'])
            elif result['time_find_start'] < values['time_find_start']\
                    and not mate_find:
                await bd_mate_update(message.from_user.id, result['user_id'])
            else:
                return
    else:
        result = await conn.fetchrow(
                        '''
                        SELECT * FROM parimate_users
                        WHERE user_id != $1 and habit_category = $2
                        and sex = $3
                        and (habit_mate_sex = $4 or
                        habit_mate_sex = 'Не имеет значения')
                        and (pari_mate_id IS NULL or pari_mate_id = $1)
                        and time_find_start IS NOT NULL
                        ORDER BY time_find_start
                        Limit 1
                        ''', message.from_user.id,
                        values['habit_category'],
                        values['habit_mate_sex'], values['sex'])
        if result is None or values['time_find_start'] is None:
            return
        else:
            mate_find = scheduler.get_job(f'send_mate_msg_{result["user_id"]}')
            if result['time_find_start'] > values['time_find_start']:
                await bd_mate_update(message.from_user.id, result['user_id'])
            elif result['time_find_start'] < values['time_find_start']\
                    and not mate_find:
                await bd_mate_update(message.from_user.id, result['user_id'])
            else:
                return
    await state.update_data(mate_id=result["user_id"])
    await send_mate_msg(values, result, state, bot)
    get_find_job = scheduler.get_job(f'mate_find_{message.from_user.id}')
    get_cancel_job = scheduler.get_job(f'mate_cancel_{message.from_user.id}')
    if get_find_job and not get_cancel_job:
        scheduler.pause_job(f'mate_find_{message.from_user.id}')
        scheduler.add_job(bd_check_cancel, trigger='interval',
                          seconds=5, id=f'mate_cancel_{message.from_user.id}',
                          kwargs={'message': message,
                                  'scheduler': scheduler})
    elif get_find_job and get_cancel_job:
        scheduler.pause_job(f'mate_find_{message.from_user.id}')
    elif get_cancel_job and not get_find_job:
        pass
    else:
        scheduler.add_job(bd_check_cancel, trigger='interval',
                          seconds=5, id=f'mate_cancel_{message.from_user.id}',
                          kwargs={'message': message,
                                  'scheduler': scheduler})


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


async def bd_chat_update(user_id: int, mate_id: int,
                         scheduler: AsyncIOScheduler,
                         state: FSMContext, bot: Bot):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
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
                get_chat_job = scheduler.get_job(f'chat_find_{user_id}')
                get_cancel_job = scheduler.get_job(f'mate_cancel_{user_id}')
                get_mate_job = scheduler.get_job(f'mate_find_{user_id}')
                if get_chat_job:
                    scheduler.remove_job(f'chat_find_{user_id}')
                if get_cancel_job:
                    scheduler.remove_job(f'mate_cancel_{user_id}')
                if get_mate_job:
                    scheduler.remove_job(f'mate_find_{user_id}')
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
            await state.clear()
            await conn.close()
    else:
        await bot.send_message(settings.bots.tech_id,
                               text='Нет чатов для пользователей')
    await conn.close()


async def bd_pari_report_create(user_id: int, pari_report: List[str],
                                report_time):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    await conn.execute('''
                       INSERT INTO parimate_reports
                       (user_id, pari_report, date, status)
                       VALUES($1, $2, $3, $4)
                       ''', user_id, pari_report, report_time,
                       'waiting')
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
    rows = await conn.fetch('''
                    SELECT user_id FROM parimate_users
                    WHERE ((time_find_start is not NULL)
                    AND (time_find_start < NOW() - INTERVAL '5' MINUTE)
                    AND (time_pari_start is NULL))
                    ''')

    await conn.close()
    return rows


async def bd_find_time_update(user_id: int):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    await conn.execute('''
                    UPDATE parimate_users SET
                    time_find_start = NOW(),
                    habit_category = 'all'
                    WHERE user_id = $1
                    ''', user_id)

    await conn.close()


async def bd_get_chat_id(chat_link: str | None = None,
                         user_id: str | None = None):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    if chat_link:
        result = await conn.fetchrow('''
                        SELECT chat_id FROM parimate_chats
                        WHERE chat_link = $1
                        ''', chat_link)
    elif user_id:
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


async def bd_last_day_select():
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    bad_result = await conn.fetch('''
                    SELECT * FROM parimate_users
                    WHERE DATE(time_pari_end) = DATE(NOW())
                    AND pari_reports < (habit_frequency/2)
                    ''')
    time.sleep(0.5)
    good_result = await conn.fetch('''
                    UPDATE parimate_users SET
                    habit_week = COALESCE(habit_week, 0) + 1,
                    pari_reports = 0
                    WHERE DATE(time_pari_end) = DATE(NOW())
                    AND pari_reports >= (habit_frequency/2)
                    RETURNING *
                    ''')
    await conn.close()
    return good_result, bad_result
