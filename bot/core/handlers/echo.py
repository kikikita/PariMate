from aiogram import Router
from aiogram.types import Message
from core.keyboards.inline import get_start_kb


router = Router()


@router.message()
async def echo(message: Message):
    await message.answer('Я тебя не понимаю(',
                         reply_markup=get_start_kb())
