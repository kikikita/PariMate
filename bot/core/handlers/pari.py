from aiogram import Bot, Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.media_group import MediaGroupBuilder
from core.keyboards.reply import (
    main_menu_kb, pari_report_cancel, remove_kb)
from core.keyboards.inline import (
    get_pari, cancel_approve, cancel_сancel, mate_report, pari_report_more,
    cancel_report_reject, pari_report_confirm)
from aiogram.fsm.context import FSMContext
from core.utils.states import Pari
from core.database.bd import (
    bd_user_select, bd_status_clear, bd_chat_delete, bd_chat_select,
    bd_pari_report_create, bd_pari_report_get, bd_pari_report_update)
from settings import settings
import ast
import datetime as dt
import time

router = Router()


@router.message(Command(commands=["pari"]))
@router.message(F.text.casefold().in_(['мои пари']))
async def pari(message: Message, state: FSMContext):
    result = await bd_user_select(message.from_user.id)
    if isinstance(result, dict) and result['time_pari_start'] is not None\
            and result['pari_mate_id'] is not None:
        pari_mate = await bd_user_select(result['pari_mate_id'])
        await state.update_data(pari_mate_id=result['pari_mate_id'])
        await message.answer(
            'Активное пари c ' +
            f'{result["time_pari_start"].strftime("%d/%m/%y")} ' +
            f'по {result["time_pari_end"].strftime("%d/%m/%y")}:' +
            f'\n\nТвоя цель: {result["habit_choice"].lower()} ' +
            f'{result["habit_frequency"]} раз(-а) в неделю' +
            f'\nПодтверждение: {result["habit_report"].lower()}'
            f'\nКоличество подтверждений: ' +
            f'{result["pari_reports"] if result["pari_reports"] is not None else 0}/' +
            f'{result["habit_frequency"]}' +
            f'\n\nЦель напарника: {pari_mate["habit_choice"].lower()} ' +
            f'{pari_mate["habit_frequency"]} раз(-а) в неделю ' +
            f'\nПодтверждение: {pari_mate["habit_report"].lower()}'
            f'\nКоличество подтверждений: ' +
            f'{pari_mate["pari_reports"] if pari_mate["pari_reports"] is not None else 0}/' +
            f'{pari_mate["habit_frequency"]}',
            reply_markup=get_pari(result['pari_chat_link'])
            )
    elif isinstance(result, dict) and result['time_pari_start'] is not None:
        await message.answer(
            'Активное пари c ' +
            f'{result["time_pari_start"].strftime("%d/%m/%y")} ' +
            f'по {result["time_pari_end"].strftime("%d/%m/%y")}:' +
            f'\n\nТвоя цель: {result["habit_choice"].lower()} ' +
            f'{result["habit_frequency"]} раз(-а) в неделю' +
            f'\nПодтверждение: {result["habit_report"].lower()}'
            f'\nКоличество подтверждений: ' +
            f'{result["pari_reports"] if result["pari_reports"] is not None else 0}/' +
            f'{result["habit_frequency"]}' +
            '\n\nНапарник отказался от участия в пари',
            reply_markup=get_pari(result['pari_chat_link'])
            )
    else:
        await message.answer('В данный момент ты не принимаешь участие в пари',
                             reply_markup=main_menu_kb())


@router.callback_query(F.data == "update_report")
async def get_pari_report(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    # if 'pari_message' in data and data['pari_message'] != []:
    #     for msg in data['pari_message']:
    #         await msg.delete()
    data['pari_message'] = []
    callback_msg = await callback.message.answer(
        "Загрузи фото, подтверждающее выполнение привычки, " +
        "либо нажми кнопку 'Отмена'",
        reply_markup=cancel_сancel())
    await state.set_state(Pari.pari_report)
    data['pari_message'].append(callback_msg)
    await state.update_data(pari_message=data['pari_message'])
    await callback.answer()


async def media_bulder(photos: list, caption: str | None = None):
    if caption is not None:
        media_group = MediaGroupBuilder(caption=caption)
    else:
        media_group = MediaGroupBuilder()
    for photo in photos:
        media_group.add_photo(photo)
    media = media_group.build()
    return media


@router.message(Pari.pari_report, F.photo)
async def photo_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    if 'pari_report' not in data:
        data['pari_report'] = []
    data["pari_report"].append(message.photo[1].file_id)

    await state.update_data(pari_report=data["pari_report"])
    await state.set_state(Pari.pari_report)
    # data['pari_message'].append(message)
    for msg in data['pari_message']:
        await msg.delete()
    reply = await message.reply(
                        'Фото загружено(-ы)',
                        reply_markup=pari_report_confirm())
    data['pari_message'].append(reply)
    await state.update_data(pari_report=data["pari_report"])


@router.callback_query(Pari.pari_report, F.data == 'send_report')
async def not_foto_handler(callback: CallbackQuery, state: FSMContext,
                           bot: Bot):
    await callback.message.delete()
    data = await state.get_data()
    report_time = dt.datetime.now()
    if len(data['pari_report']) > 1:
        media = await media_bulder(
            data['pari_report'], 'Отчет от ' +
            f'{report_time.strftime("%d/%m/%y %H:%M")} сформирован')
        await callback.message.answer_media_group(media)
    else:
        await callback.message.answer_photo(
            data['pari_report'][0], 'Отчет от ' +
            f'{report_time.strftime("%d/%m/%y %H:%M")} сформирован')
    await bd_pari_report_create(callback.from_user.id,
                                str(data['pari_report']),
                                report_time)
    await callback.message.answer(
                        'Подтверждение отправлено',
                        reply_markup=remove_kb)
    pari_mate_id = (
        await bd_user_select(callback.from_user.id))['pari_mate_id']
    await bot.send_message(
        pari_mate_id,
        'Напарник загрузил новое подтверждение, показать?',
        reply_markup=pari_report_more())

    # for msg in data['pari_message']:
    #     await msg.delete()
    await state.clear()
    await callback.answer()
# @router.message(Pari.pari_report,
#                 F.text.casefold().in_(['отправить на проверку', 'отмена']))
# async def not_foto_handler(message: Message, state: FSMContext, bot: Bot):
#     data = await state.get_data()
#     if message.text.lower() == 'отправить на проверку':
#         report_time = dt.datetime.now()
#         if len(data['pari_report']) > 1:
#             media = await media_bulder(
#                 data['pari_report'], 'Отчет от ' +
#                 f'{report_time.strftime("%d/%m/%y %H:%M")} сформирован')
#             await message.answer_media_group(media)
#         else:
#             await message.answer_photo(
#                 data['pari_report'][0], 'Отчет от ' +
#                 f'{report_time.strftime("%d/%m/%y %H:%M")} сформирован')
#         await bd_pari_report_create(message.from_user.id,
#                                     str(data['pari_report']),
#                                     report_time)
#         await message.answer('Подтверждение отправлено',
#                              reply_markup=remove_kb)
#         pari_mate_id = (
#             await bd_user_select(message.from_user.id))['pari_mate_id']
#         await bot.send_message(
#             pari_mate_id,
#             'Напарник загрузил новое подтверждение, показать?',
#             reply_markup=pari_report_more())

#     for msg in data['pari_message']:
#         await msg.delete()
#     await message.delete()
#     await state.clear()


@router.callback_query(F.data == "mate_report")
async def get_mate_reports(callback: CallbackQuery, state: FSMContext):
    user = await bd_user_select(callback.from_user.id)
    mate_id = user['pari_mate_id']
    result = await bd_pari_report_get(mate_id, status='waiting')
    if result:
        photos = ast.literal_eval(result['pari_report'])
        if len(photos) > 1:
            media = await media_bulder(
                photos,
                'Отчет напарника от ' +
                f'{result["date"].strftime("%d/%m/%y %H:%M")}')
            await callback.message.answer_media_group(media)
            time.sleep(0.2)
            await callback.message.answer(
                                    'Подтвердить отчет?',
                                    reply_markup=mate_report())
        else:
            await callback.message.answer_photo(
                photos[0],
                'Отчет напарника от ' +
                f'{result["date"].strftime("%d/%m/%y %H:%M")}')
            time.sleep(0.2)
            await callback.message.answer(
                                    'Подтвердить отчет?',
                                    reply_markup=mate_report())
        await state.set_state(Pari.mate_report)
        await state.update_data(mate_report=result,
                                pari_mate_id=mate_id)
    else:
        await callback.message.delete()
        await callback.message.answer('Нет новых подтверждений')
    await callback.answer()


@router.callback_query(Pari.mate_report, F.data == "report_approve")
async def approve_mate_reports(callback: CallbackQuery, state: FSMContext,
                               bot: Bot):
    data = await state.get_data()
    mate_report = data['mate_report']
    await callback.message.delete()
    await bd_pari_report_update(mate_report['report_id'], 'approved')
    await callback.message.answer('Отчет подтвержден')
    await callback.message.answer('Загрузить следующий?',
                                  reply_markup=pari_report_more())
    await bot.send_message(
        data['pari_mate_id'],
        'Напарник подтвердил ваш отчет от ' +
        f'{mate_report["date"].strftime("%d/%m/%y %H:%M")}')
    await callback.answer()


@router.callback_query(Pari.mate_report, F.data == "report_reject")
async def reject_mate_reports(callback: CallbackQuery, state: FSMContext):
    reject_msg = await callback.message.edit_text(
        'Укажите причину, по которой вы отклонили фотоотчет',
        reply_markup=cancel_report_reject())

    await state.set_state(Pari.reject_reason)
    await state.update_data(pari_message=reject_msg.message_id)
    await callback.answer()


@router.callback_query(Pari.reject_reason, F.data == "cancel_report_reject")
async def reject_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Подтвердить отчет?',
                                     reply_markup=mate_report())
    await state.set_state(Pari.mate_report)
    await callback.answer()


@router.message(Pari.reject_reason)
async def reason_report_reject(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    mate_report = data['mate_report']
    await bot.delete_message(message.chat.id, data['pari_message'])
    await bd_pari_report_update(mate_report['report_id'], 'rejected',
                                reason=message.text)
    await bot.send_message(
        data['pari_mate_id'],
        'Напарник отклонил ваш отчет от ' +
        f'{mate_report["date"].strftime("%d/%m/%y %H:%M")}' +
        f'\nПричина: {message.text}')
    await message.answer('Отчет отклонен')
    await message.answer('Загрузить следующий?',
                         reply_markup=pari_report_more())


@router.message(Pari.pari_report)
async def wrong_report(message: Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    if 'pari_report' not in data:
        msg = await message.answer(
            "Загрузи фото, подтверждающее выполнение привычки, " +
            "либо нажми кнопку 'Отмена'",
            reply_markup=pari_report_cancel())
    else:
        msg = await message.answer(
            "Загрузи фото, подтверждающее выполнение привычки, " +
            "либо нажми кнопку 'Отмена'",
            reply_markup=pari_report_confirm())
    data['pari_message'].append(msg)
    await state.update_data(pari_message=data['pari_message'])


@router.callback_query(F.data == "pari_сancel")
async def pari_cancel(callback: CallbackQuery):
    await callback.message.answer(
        "Ты уверен, что желаешь досрочно завершить пари?",
        reply_markup=cancel_approve())
    await callback.answer()


@router.callback_query(F.data == "сancel_no")
async def pari_cancel_no(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if 'pari_message' in data and data['pari_message'] != []\
            and type(data['pari_message']) is not int:
        for msg in data['pari_message']:
            await msg.delete()
    else:
        await callback.message.delete()
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "сancel_yes")
async def pari_cancel_yes(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Укажи причину по которой ты желаешь завершить пари",
        reply_markup=cancel_сancel())
    await state.set_state(Pari.pari_cancel)
    await callback.answer()


@router.message(Pari.pari_cancel)
async def pari_cancel_end(message: Message, state: FSMContext, bot: Bot):
    await message.answer(
        "Пари завершено",
        reply_markup=main_menu_kb())
    chat = await bd_chat_select(message.from_user.id)
    if isinstance(chat, dict):
        if message.from_user.id != settings.bots.admin_id:
            await bot.ban_chat_member(
                str(chat['chat_id']), message.from_user.id)

        if chat['user_1'] is not None and chat['user_2'] is not None:
            await bot.send_message(str(chat['chat_id']),
                                   'Ваш напарник досрочно завершил пари')

    await state.clear()
    await bd_status_clear(message.from_user.id, message.text)
    await bd_chat_delete(message.from_user.id)
    await bot.unban_chat_member(
                str(chat['chat_id']), message.from_user.id,
                only_if_banned=True)
