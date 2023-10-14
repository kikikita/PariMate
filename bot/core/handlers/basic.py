from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message
from core.keyboards.reg_kb import get_reply_keyboard

router = Router()


@router.message(Command("start"))
async def get_start(message: Message, bot: Bot):
    await message.answer(
            f'Привет, {message.from_user.first_name}!' +
            '\nДобро пожаловать в PariMate! Здесь ты найдешь мотивацию 💪' +
            ' и сможешь соревноваться с людьми в достижении своих целей.'
            '\nВыбирай желаемую привычку, которую хочешь развить, а мы'
            ' подберем тебе оппонента со схожей целью и расписанием 🕑.'
            '\nВперед к новым победам и достижениям !',
            reply_markup=get_reply_keyboard()
            )
