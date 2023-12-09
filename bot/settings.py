from environs import Env
from dataclasses import dataclass
from typing import List


@dataclass
class Bots:
    bot_token: str
    admin_id: int
    tech_id: str
    moder_ids: List[int]


@dataclass
class Settings:
    bots: Bots


def get_settings(path: str):
    env = Env()
    env.read_env(path)

    return Settings(
        bots=Bots(
            bot_token=env.str("TOKEN"),
            admin_id=env.int("ADMIN_ID"),
            tech_id=env.str("TECH_ID"),
            moder_ids=[int(x) for x in env.list("MODERS_IDS")]
        )
    )


settings = get_settings('.env')
print(settings)
