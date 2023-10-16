from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from core.keyboards.inline import get_start_kb

router = Router()


@router.message(Command("start"))
async def get_start(message: Message):
    await message.answer(
            f'Привет, {message.from_user.first_name}!' +
            '\nДобро пожаловать в PariMate! Здесь ты найдешь мотивацию 💪' +
            ' и сможешь соревноваться с людьми в достижении своих целей.'
            '\nВыбирай желаемую привычку, которую хочешь развить, а мы'
            ' подберем тебе оппонента со схожей целью и расписанием 🕑.'
            '\nВперед к новым победам и достижениям !',
            reply_markup=get_start_kb()
            )


@router.message(F.text == 'Узнать подробнее о проекте')
async def get_info(message: Message):
    await message.answer(
            'Проект направлен на мотивацию пользователей' +
            ' к достижению своих целей и развитие полезных' +
            ' привычек через социальное взаимодействие и азарт.',
            reply_markup=get_start_kb()
            )
