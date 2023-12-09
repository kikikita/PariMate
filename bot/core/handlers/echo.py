from aiogram import Router
from aiogram.types import Message
# from core.keyboards.reply import remove_kb
from core.filters.chat_type import ChatTypeFilter


router = Router()


@router.message(ChatTypeFilter(chat_type=["private"]))
async def echo(message: Message):
    await message.delete()
