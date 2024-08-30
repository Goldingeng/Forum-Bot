from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InputMediaVideo, InputMediaAudio, InputMediaDocument
from aiogram import types
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from src.keyboards import menu_markup, canel_markup
from src.keyboards.callback import PostCallback
from aiogram.utils.media_group import MediaGroupBuilder
from dotenv import load_dotenv
from ..utils.container import *
from ..utils.postcheck import *
import json
from aiogram_media_group import media_group_handler
from aiogram.utils.media_group import MediaGroupBuilder
from ..utils.post import *

load_dotenv()


menu_router = Router(name="menu")


@menu_router.message(F.text == "/menu")
async def menu_handler(message: Message) -> None:
    if message.chat.type != "private":
        await message.answer("Эта команда доступна только в личных сообщениях.")
        return

    await message.answer(
        "Добро пожаловать! Это бот для постинга постов на канал.",
        parse_mode="HTML", reply_markup=menu_markup(message.from_user.id)
    )

@menu_router.callback_query(PostCallback.filter())
async def post_callback_handler(query: CallbackQuery, state: FSMContext) -> None:
    await query.message.edit_text("Напишите свой пост:", reply_markup=canel_markup(query.from_user.id))
    await state.set_state(PostState.waiting_for_post)


@menu_router.message(F.media_group_id, PostState.waiting_for_post)
@media_group_handler
async def album_handler(messages: List[types.Message], state: FSMContext, bot: Bot, session: AsyncSession):
    await handle_media_group(messages, state, bot, session)


@menu_router.message(PostState.waiting_for_post)
async def handle_user_post(message: Message, state: FSMContext, bot: Bot, session: AsyncSession):
    await handle_single_message(message, state, bot, session)


async def handle_single_message(message: types.Message, state: FSMContext, bot: Bot, session: AsyncSession):
    user_id = message.from_user.id
    caption = message.caption if message.caption else message.text
    name = message.from_user.first_name
    post_id = message.message_id

    if not await process_message(bot, message, state, user_id, name, caption, session):
        return

    media = []
    photo_urls = []

    if message.photo:
        photo = message.photo[-1]
        photo_file = await bot.get_file(photo.file_id)
        photo_file_bytes = await bot.download_file(photo_file.file_path)
        
        photo_url = f"https://api.telegram.org/file/bot{bot.token}/{photo_file.file_path}"
        photo_urls.append(photo_url)
        
        if contains_nudity(photo_file_bytes.read()):
            photo_links_json = json.dumps(photo_urls)
            
            await message.answer("Сообщение содержит неподобающий контент.")
            await send_admin_notification(bot, user_id, name, caption, post_id, session, photo_links_json, json.dumps(photo.file_id))
            ban_user(user_id)
            await state.clear()
            return
        
        media.append(InputMediaPhoto(media=photo.file_id, caption=caption))
    
    if message.video:
        media.append(InputMediaVideo(media=message.video.file_id, caption=caption))
    if message.audio:
        media.append(InputMediaAudio(media=message.audio.file_id, caption=caption))
    if message.voice:
        media.append(InputMediaAudio(media=message.voice.file_id, caption=caption))
    if message.document:
        media.append(InputMediaDocument(media=message.document.file_id, caption=caption))

    if media:
        await send_scheduled_post_media(bot,message.from_user.id, media)
    else:
        await send_scheduled_post(bot, caption, message.from_user.id)
        await message.answer("Ваш пост принят и вскоре будет опубликован!")


    await state.clear()


async def handle_media_group(messages: List[types.Message], state: FSMContext, bot: Bot, session: AsyncSession):
    caption = messages[0].caption if messages[0].caption else ""
    user_id = messages[0].from_user.id
    name = messages[0].from_user.first_name
    post_id = messages[0].message_id 

    if not await process_message(bot, messages[-1], state, user_id, name, caption, session):
        return

    photo_urls = []
    has_nudity = False
    photos = []
    for message in messages:
        if message.photo:
            photo = message.photo[-1]
            photos.append(photo.file_id)
            photo_file = await bot.get_file(photo.file_id)
            photo_file_path = photo_file.file_path

            
            photo_url = f"https://api.telegram.org/file/bot{bot.token}/{photo_file_path}"
            photo_urls.append(photo_url)


            photo_file_bytes = await bot.download_file(photo_file_path)
            if contains_nudity(photo_file_bytes.read()):
                has_nudity = True

    if has_nudity:
        photos_str = json.dumps(photos)
        
        photo_links = "\n".join(photo_urls)
        await send_admin_notification(bot, user_id, name, caption, post_id, session, photo_links, photos_str)
        await messages[-1].answer(f"Сообщение содержит неподобающий контент.")
        ban_user(user_id)
        await state.clear()
        return

    media_group_builder = MediaGroupBuilder(caption=caption)
    

    for message in messages:
        if message.document:
            media_group_builder.add_document(message.document.file_id)
        if message.photo:
            media_group_builder.add_photo(message.photo[-1].file_id)

    media_group = media_group_builder.build()

    await send_scheduled_post_media(bot, message.from_user.id, media_group)
    await message.answer("Ваш пост принят и вскоре будет опубликован!")
    #await messages[-1].answer_media_group(media_group.build(), reply_markup=menu_markup(user_id))

    await state.clear()
