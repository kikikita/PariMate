import asyncpg
from aiogram.types import Message
from dotenv import dotenv_values
# import asyncio


config = dotenv_values('.env')

USER = config['user']
PSWD = config['password']
DB = config['database']
HOST = config['host']


async def bd_interaction(message: Message, values: list):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    await conn.execute('''
                       INSERT INTO parimate_users(user_id, name, age, sex)
                       VALUES($1, $2, $3, $4)
                       ''', message.from_user.id,
                       values['name'], int(values['age']), values['sex'])
    await conn.close()


async def bd_user_check(message: Message):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    result = await conn.fetchrow('''
                    SELECT * FROM parimate_users WHERE user_id = $1
                    ''', message.from_user.id)
    await conn.close()

    if result is not None:
        pass
    else:
        return False


async def bd_habit_update(message: Message, values: list):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    await conn.execute('''
                       UPDATE parimate_users SET habit_category = $2,
                       habit_choice = $3, habit_frequency = $4,
                       habit_report = $5,
                       habit_mate_sex = $6 WHERE user_id = $1
                       ''', message.from_user.id,
                       values['habit_category'], values['habit_choice'],
                       int(values['habit_frequency']),
                       values['habit_report'], values['habit_mate_sex'])

    await conn.close()


async def bd_user_select(message: Message):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    result = await conn.fetchrow('''
                    SELECT * FROM parimate_users WHERE user_id = $1
                    ''', message.from_user.id)
    await conn.close()

    if result is not None:
        return dict(result)
    else:
        return False


async def bd_mate_find(message: Message, values: list, sex: str):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB,
                                 host=HOST)
    result = await conn.fetchrow(
                    '''
                    SELECT * FROM parimate_users
                    WHERE user_id != $1 and habit_category = $2
                    and habit_report = $3 and sex = $4
                    and habit_mate_sex = $5 Limit 1
                    ''', message.from_user.id,
                    values['habit_category'], values['habit_report'],
                    values['habit_mate_sex'], sex)
    await conn.close()

    if result is not None:
        return dict(result)
    else:
        return False
# asyncio.run(bd_user_select(323718009))
