from aiogram import Router
from aiogram.types import ChatMemberUpdated
from aiogram.filters import ChatMemberUpdatedFilter, IS_MEMBER, IS_NOT_MEMBER


router = Router()


@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def on_user_join(event: ChatMemberUpdated):
    # await event.answer(views.join_message(event.new_chat_member.user.first_name))
    await event.answer(f'Привет, {(event.new_chat_member.user.first_name)}')


@router.chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER))
async def on_user_left(event: ChatMemberUpdated):
    # await event.answer(views.left_message(event.old_chat_member.user.first_name))
    await event.answer(f'Прощай, {(event.old_chat_member.user.first_name)}')
