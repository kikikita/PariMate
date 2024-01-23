from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from core.filters.chat_type import ChatTypeFilter


router = Router()


@router.message(Command(commands=["help"]),
                ChatTypeFilter(chat_type=["group", "supergroup"]))
async def get_info(message: Message | CallbackQuery,
                   state: FSMContext):
    await state.clear()
    await message.answer(
            '/pari -> доступный функционал:' +
            '\n\n🔘 Досрочно завершить пари' +
            '\n(досрочное завершения пари)'
            '\n🔘 Перейти в совместный чат' +
            '\n(кнопка-ссылка в чат с напарником)'
            '\n🔘 Отчеты напарника' +
            '\n(проверка новых отчетов напарника)' +
            '\n🔘 Подтвердить выполнение привычки ' +
            '\n(загрузка отчетов о привычках, ' +
            'формат: фото/видео/кружочки/текст)' +
            '\n\nПо вопросам работы бота: @kikikita1337')


@router.message(Command(commands=["help"]),
                ChatTypeFilter(chat_type=["private"]))
@router.callback_query(F.data.startswith("help"))
async def get_private_info(message: Message | CallbackQuery,
                           state: FSMContext):
    await state.clear()
    if isinstance(message, CallbackQuery):
        await message.answer()
        message = message.message
    await message.answer(
            '/menu -> главное меню:' +
            '\n\n🔘 Найти мотивацию' +
            '\n(поиск напарника по привычки)' +
            '\n🔘 Мои пари' +
            '\n(раздел с активным пари)' +
            '\n🔘 Профиль' +
            '\n(редактирование профиля)' +
            '\n🔘 Помощь' +
            '\n(техническая поддержка и навигация)' +
            '\n\n/pari -> управление пари:' +
            '\n\n🔘 Досрочно завершить пари' +
            '\n(досрочное завершения пари)'
            '\n🔘 Перейти в совместный чат' +
            '\n(кнопка-ссылка в чат с напарником)'
            '\n🔘 Отчеты напарника' +
            '\n(проверка новых отчетов напарника)' +
            '\n🔘 Подтвердить выполнение привычки ' +
            '\n(загрузка отчетов о привычках, ' +
            'формат: фото/видео/кружочки/текст)' +
            '\n\n/profile -> профиль:' +
            '\n\n🔘 Изменить данные о себе' +
            '\n(редактирование профиля)'
            '\n\nПо вопросам работы бота: @kikikita1337')
