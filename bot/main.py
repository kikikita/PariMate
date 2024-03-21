from aiogram import Bot, Dispatcher
from core.handlers import (
    basic, registration, habit, pari, profile,
    find, events, echo, group_games, admin, help)
import asyncio
import logging
from settings import settings
from core.utils.commands import set_commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from core.utils.notifications import (
    send_statistics, send_notifications, change_category_find,
    last_day_notify, check_ignore_reports)
from core.middlewares.scheduler import SchedulerMiddleware
from core.database.bd import match_partners


async def start_bot(bot: Bot):
    await set_commands(bot)
    await bot.send_message(settings.bots.admin_id, text='Бот запущен!')


async def stop_bot(bot: Bot):
    await bot.send_message(settings.bots.admin_id, text='Бот остановлен!')


async def start():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - [%(levelname)s] - %(name)s - "
                        "(%(filename)s).%(funcName)s(%(lineno)d) -%(message)s")
    bot = Bot(token=settings.bots.bot_token)
    dp = Dispatcher()
    scheduler = AsyncIOScheduler()

    dp.update.middleware.register(SchedulerMiddleware(scheduler))
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    dp.include_routers(help.router,
                       registration.router, basic.router,
                       profile.router, pari.router,
                       habit.router, events.router,
                       find.router
                       )
    dp.include_router(admin.router)
    dp.include_router(echo.router)
    dp.include_router(group_games.router)

    scheduler.add_job(send_statistics, trigger='interval',
                      hours=12, start_date='2023-11-10 09:00:00',
                      kwargs={'bot': bot})
    scheduler.add_job(send_notifications, trigger='interval',
                      hours=1, start_date='2023-11-10 00:00:00',
                      kwargs={'bot': bot})
    scheduler.add_job(change_category_find, trigger='interval',
                      minutes=30, kwargs={'bot': bot})
    scheduler.add_job(last_day_notify, trigger='interval',
                      hours=1, start_date='2023-11-10 00:05:00',
                      kwargs={'bot': bot})
    scheduler.add_job(check_ignore_reports, trigger='interval',
                      hours=1, start_date='2023-11-10 00:40:00',
                      kwargs={'bot': bot})
    scheduler.add_job(match_partners, trigger='interval',
                      seconds=30, kwargs={'bot': bot})
    try:
        scheduler.start()
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(start())
