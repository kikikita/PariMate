from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from core.keyboards.inline import get_start_kb, get_main_menu
from aiogram.fsm.context import FSMContext
from core.filters.chat_type import ChatTypeFilter


router = Router()


@router.message(Command(commands=["start"]),
                ChatTypeFilter(chat_type=["private"]))
async def get_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
            f'Привет, <b>{message.from_user.first_name}!</b>' +
            '\n\nДобро пожаловать в PariMate! Здесь ты найдешь мотивацию 💪' +
            ' и станешь ближе в достижении своих целей 🏆.'
            '\n\n<i>Как это работает?</i>' +
            '\n1. Подумай, что бы ты хотел изменить в своей жизни? ' +
            '\nВыбери цель, и на ее основе мы подберем тебе напарника, ' +
            'с которым вы заключите пари 🤝' +
            '\n\n2. Просто подтверждай выполнение цели по выбранному тобой ' +
            'расписанию, а также не забывай подтверждать отчеты партнера 🕙' +
            '\n\n3. После 21 дня успешной работы над достижением цели, ' +
            'ты сможешь принять участие в розыгрыше сертификатов Озон 🎉' +
            '\n\nЖелаем не опускать руки на пути к самосовершенствованию!' +
            '\nВсе получится, мы в этом уверены 😊',
            parse_mode=ParseMode.HTML,
            reply_markup=get_start_kb()
            )


@router.message(Command(commands=["menu"]),
                ChatTypeFilter(chat_type=["private"]))
@router.callback_query(
    F.data.startswith("menu"), ChatTypeFilter(chat_type=["private"]))
async def get_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
            'Главное меню',
            reply_markup=get_main_menu()
            )


@router.message(Command(commands=["menu", 'profile']),
                ChatTypeFilter(chat_type=["group", "supergroup"]))
async def get_group_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        'В групповом чате доступны следующие команды:' +
        '\n\n/pari -> Управление пари'
        '\n/help -> Помощь'
        '\n\nЧтобы получить доступ к полному меню, ' +
        'напиши эту команду в чате с ботом')


@router.message(Command(commands=["help"]),
                ChatTypeFilter(chat_type=["group", "supergroup"]))
@router.message(F.text.casefold().in_(['помощь']),
                ChatTypeFilter(chat_type=["group", "supergroup"]))
async def get_info(message: Message, state: FSMContext):
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
@router.message(F.text.casefold().in_(['помощь']),
                ChatTypeFilter(chat_type=["private"]))
async def get_private_info(message: Message, state: FSMContext):
    await state.clear()
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
