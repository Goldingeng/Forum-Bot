from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InputMediaVideo, InputMediaAudio, InputMediaDocument
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from typing import List
from src.keyboards.callback import BanCallback, UnBanCallback, SkipCallback
from src.database.users import User
from src.database.admin import Admin
from src.database.gets import Gets
from sqlalchemy.ext.asyncio import AsyncSession
from src.keyboards import unban_markup, ban_markup
from aiogram.utils.media_group import MediaGroupBuilder
from sqlalchemy.future import select
import json
from ..utils.post import *

admin_router = Router(name="admin")

@admin_router.callback_query(BanCallback.filter())
async def ban(query: CallbackQuery, session: AsyncSession):
    user_id = BanCallback(user_id=int(query.data.split(':')[1])).user_id

    admin = await Admin.get(session, query.from_user.id)

    if admin:
        await User.ban(session, user_id, admin_id=query.from_user.id)
        await query.message.edit_text(f"Пользователь {user_id} забанен!", reply_markup=unban_markup(user_id=user_id))
    else:
        await query.answer("Ты как это нажал?", True)

@admin_router.callback_query(UnBanCallback.filter())
async def un_ban(query: CallbackQuery, session: AsyncSession):
    user_id = UnBanCallback(user_id=int(query.data.split(':')[1])).user_id

    admin = await Admin.get(session, query.from_user.id)

    if admin:
        await User.unban(session, user_id, admin_id=query.from_user.id)
        await query.message.edit_text(f"Пользователь {user_id} разбанен!!", reply_markup=ban_markup(user_id=user_id, post_id=0))
    else:
        await query.answer("Ты как это нажал?", True)


@admin_router.callback_query(SkipCallback.filter())
async def skip(query: CallbackQuery, bot: Bot, session: AsyncSession):
    try:
        post_id = int(query.data.split(':')[2])
    except (IndexError, ValueError):
        await query.answer("Не удалось извлечь идентификатор поста.")
        return

    post = await Gets.get(session, post_id)

    if not post:
        await query.answer("Пост не найден.")
        return

    messageAdmin = query.message.text
    text = post.text
    media_ids_json = post.media

    if media_ids_json:
        media_ids = json.loads(media_ids_json)
        media_group_builder = MediaGroupBuilder(caption=text)
        
        for media_id in media_ids:
            if media_id.startswith('AgACAgIAAxkBAA'):
                print(f"Photo media ID: {media_id}")  # Use f-string for clarity
                media_group_builder.add_photo(media_id)
            else:
                print(f"Document media ID: {media_id}")  # Use f-string for clarity
                media_group_builder.add_document(media_id)

        media_group = media_group_builder.build()

        await bot.send_message(chat_id=query.from_user.id, text="Администратор одобрил пост!", reply_to_message_id=post_id)

        try:
            await send_scheduled_post_media(bot, post.user_id, media_group)
        except Exception as e:
            await bot.send_message(chat_id=query.from_user.id, text=f"Ошибка при отправке медиа: {e}")
    else:
        await send_scheduled_post(bot, text, post.user_id)

    await query.message.edit_text(f"Пост одобрен администратором {query.from_user.first_name} ({query.from_user.id})\n\n{messageAdmin}")
