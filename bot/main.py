from aiogram import Bot, Dispatcher
from core.handlers import (
    basic, registration, habit, pari, profile, 
    find, events, echo, group_games)
import asyncio
import logging
from settings import settings
from core.utils.commands import set_commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from core.utils.notifications import (
    send_notifications, change_time_find, last_day_notify)
from core.middlewares.scheduler import SchedulerMiddleware


async def start_bot(bot: Bot):
    await set_commands(bot)
    # await bot.send_message(settings.bots.admin_id, text='Бот запущен!')


# async def stop_bot(bot: Bot):
#     await bot.send_message(settings.bots.admin_id, text='Бот остановлен!')


async def start():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - [%(levelname)s] - %(name)s - "
                        "(%(filename)s).%(funcName)s(%(lineno)d) -%(message)s")
    bot = Bot(token=settings.bots.bot_token)
    dp = Dispatcher()
    scheduler = AsyncIOScheduler()

    dp.update.middleware.register(SchedulerMiddleware(scheduler))
    dp.startup.register(start_bot)
    # dp.shutdown.register(stop_bot)

    dp.include_routers(registration.router, basic.router,
                       profile.router, pari.router,
                       habit.router, events.router,
                       find.router
                       )
    dp.include_router(echo.router)
    dp.include_router(group_games.router)

    scheduler.add_job(send_notifications, trigger='interval',
                      hours=1, start_date='2023-11-10 00:00:00',
                      kwargs={'bot': bot})
    scheduler.add_job(change_time_find, trigger='interval',
                      minutes=5)
    scheduler.add_job(last_day_notify, trigger='cron', hour='20', minute='15',
                      kwargs={'bot': bot})
    try:
        scheduler.start()
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(start())
