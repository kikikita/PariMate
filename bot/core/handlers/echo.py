from aiogram import Router
from aiogram.types import Message
from core.keyboards.reply import remove_kb
from core.filters.chat_type import ChatTypeFilter


router = Router()


@router.message(ChatTypeFilter(chat_type=["private"]))
async def echo(message: Message):
    await message.answer('Я тебя не понимаю(',
                         reply_markup=remove_kb)
    await message.delete()
