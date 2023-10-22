import asyncpg
from dotenv import dotenv_values

config = dotenv_values('.env')

USER = config['user']
PSWD = config['password']
DB = config['database']
HOST = config['host']

async def bd_interaction(values: list):
    conn = await asyncpg.connect(user=USER, password=PSWD, database=DB, host=HOST)
    await conn.execute('''
                       INSERT INTO parimate_test_docker(name, age, sex, category) VALUES($1, $2, $3, $4)
                       ''', values['name'], int(values['age']), values['sex'], values['category'])

    await conn.close()

