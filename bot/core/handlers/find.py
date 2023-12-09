from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery
from core.keyboards.inline import pari_find_start, pari_find
from core.database.bd import (
    bd_time_find_update,
    bd_habit_update, bd_mate_find, bd_user_select, bd_status_clear,
    bd_chat_update, bd_chat_delete, bd_notify_update)
from core.filters.chat_type import ChatTypeFilter
from aiogram.fsm.context import FSMContext


router = Router()
router.message.filter(
    ChatTypeFilter(chat_type=["private"])
)


# async def state_fill(user_id: int, state: FSMContext):
#     data = await bd_user_select(user_id)
#     data['habit_notification_day'] = ast.literal_eval(
#             data['habit_notification_day'])
#     data['habit_notification_time'] = ast.literal_eval(
#             data['habit_notification_time'])
#     await state.update_data(data)
#     return data

#find_cancel #find_accept #find_decline
@router.callback_query(F.data.startswith("find_start"))
async def find_start(callback: CallbackQuery):
    await callback.message.edit_text(
        '⏳ Подбираем партнера по привычке...' +
        '\n✉ Сообщим, как будет готово',
        reply_markup=pari_find())
    await bd_time_find_update(callback.from_user.id)
    await callback.answer()


#find_cancel
@router.callback_query(F.data.startswith("find_cancel"))
async def find_cancel(callback: CallbackQuery):
    user = await bd_status_clear(callback.from_user.id)
    days_string = (str(user["habit_notification_day"])[1:-1]
                   .replace("'", ""))
    time_string = (str(user["habit_notification_time"])[1:-1]
                   .replace("'", ""))
    await callback.message.edit_text('Поиск отменен')
    await callback.message.answer(
        f'Твои настройки привычки:'
        f'\n\n🎯 Цель: {user["habit_choice"]}' +
        f'\n📅 Регулярность: {days_string}' +
        f'\n🔔 Время напоминаний: {time_string}' +
        f'\n🚻 Пол партнера: {user["habit_mate_sex"]}',
        reply_markup=pari_find_start()
    )

# async def pari_mate_find(message: Message, state: FSMContext,
#                          scheduler: AsyncIOScheduler, bot: Bot):
#     data = await bd_user_select(message.from_user.id)
#     if message.text == 'Отменить поиск':
#         await message.answer('Поиск отменен')
#         await bd_status_clear(message.from_user.id)
#         await message.answer(
#             'С напарником какого пола ты бы хотел заключить пари?',
#             reply_markup=mate_kb())
#         await state.set_state(Habit.habit_mate_sex)
#         get_find_job = scheduler.get_job(f'mate_find_{message.from_user.id}')
#         get_cncl_job = scheduler.get_job(f'mate_cancel_{message.from_user.id}')
#         if get_find_job and get_cncl_job:
#             scheduler.remove_job(f'mate_find_{message.from_user.id}')
#             scheduler.remove_job(f'mate_cancel_{message.from_user.id}')
#         elif get_find_job and not get_cncl_job:
#             scheduler.remove_job(f'mate_find_{message.from_user.id}')
#         elif not get_find_job and get_cncl_job:
#             scheduler.remove_job(f'mate_cancel_{message.from_user.id}')
#         else:
#             pass

#     elif message.text == 'Отказаться':
#         await message.answer('Вы отказались от пари')
#         await bd_status_clear(message.from_user.id)
#         await message.answer(
#             'С напарником какого пола ты бы хотел заключить пари?',
#             reply_markup=mate_kb())
#         await state.set_state(Habit.habit_mate_sex)
#         await bd_chat_delete(message.from_user.id)
#         get_find_job = scheduler.get_job(f'mate_find_{message.from_user.id}')
#         get_cncl_job = scheduler.get_job(f'mate_cancel_{message.from_user.id}')
#         if get_find_job and get_cncl_job:
#             scheduler.remove_job(f'mate_find_{message.from_user.id}')
#             scheduler.remove_job(f'mate_cancel_{message.from_user.id}')
#         elif get_find_job and not get_cncl_job:
#             scheduler.remove_job(f'mate_find_{message.from_user.id}')
#         elif not get_find_job and get_cncl_job:
#             scheduler.remove_job(f'mate_cancel_{message.from_user.id}')
#         else:
#             pass

#     elif message.text == 'Подтвердить пари':
#         get_job = scheduler.get_job(f'chat_find_{message.from_user.id}')
#         if not get_job:
#             scheduler.add_job(
#                 bd_chat_update, trigger='interval',
#                 seconds=5, id=f'chat_find_{message.from_user.id}',
#                 kwargs={'user_id': message.from_user.id,
#                         'mate_id': data['pari_mate_id'],
#                         'scheduler': scheduler,
#                         'state': state,
#                         'bot': bot})
#         await message.answer('Ожидаем подтверждение от напарника...')
#         await state.set_state(Habit.remove_confirm)

#     else:
#         get_job = scheduler.get_job(f'mate_find_{message.from_user.id}')
#         if not get_job:
#             scheduler.add_job(
#                 bd_mate_find, trigger='interval',
#                 seconds=1, id=f'mate_find_{message.from_user.id}',
#                 kwargs={'message': message,
#                         'scheduler': scheduler,
#                         'state': state,
#                         'bot': bot})


# @router.message(Habit.remove_confirm,
#                 F.text.casefold().in_(['отказаться', 'отменить поиск']))
# async def remove_confirm(message: Message, state: FSMContext,
#                          scheduler: AsyncIOScheduler):
#     get_job = scheduler.get_job(f'mate_cancel_{message.from_user.id}')
#     if get_job:
#         scheduler.remove_job(f'mate_cancel_{message.from_user.id}')
#     await bd_status_clear(message.from_user.id)
#     await bd_chat_delete(message.from_user.id)
#     await message.answer('Вы отказались от пари')
#     await message.answer(
#         'С напарником какого пола ты бы хотел заключить пари?',
#         reply_markup=mate_kb())
#     await state.set_state(Habit.habit_mate_sex)


# @router.message(Habit.remove_confirm)
# async def incorrect_remove_confirm(message: Message, state: FSMContext):
#     if message.text == 'Подтвердить пари':
#         await message.answer('Вы уже подтвердили пари')
#     await message.answer('Ожидаем подтверждение от напарника...')