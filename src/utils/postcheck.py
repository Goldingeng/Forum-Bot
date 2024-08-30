import datetime
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from src.database.users import User
from src.database.gets import Gets
from ..config import ADMIN_CHAT_ID, channel_id
from .container import *
from ..keyboards import ban_markup, help_markup
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import json
import re

SPAM_LIMIT = 5  
SPAM_PERIOD = 10  
POST_LIMIT_PERIOD = 600 
POST_MIN_LENGTH = 90

user_message_count = {}
user_last_post_time = {}  
user_ban_list = {}  
BAN_DURATION = 10

class PostState(StatesGroup):
    waiting_for_post = State()

async def is_user_subscribed(bot: Bot, user_id: int) -> bool:
    try:
        chat_member = await bot.get_chat_member(channel_id, user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Ошибка проверки подписки пользователя {user_id}: {e}")
        return False

async def process_message(bot: Bot, message: Message, state: FSMContext, user_id: int, name: str, text: str, session: AsyncSession):
    post_id = message.message_id 

    if not await is_user_subscribed(bot, user_id):
        await message.answer(f"Вы должны быть подписаны на канал, чтобы отправлять сообщения.", reply_markup=help_markup())
        return

    if is_user_banned(user_id):
        await message.answer(f"Вам запрещено отправлять посты на следующие {BAN_DURATION} минут.")
        return

    user = await User.get(session, user_id)
    if user and user.ban_status:
        await message.answer("Вы забанены в системе. Пожалуйста, обратитесь к администратору.")
        return

    if not is_valid_post(text):
        await message.answer(f"Ваше сообщение не соответствует требованиям. Оно должно содержать минимум {POST_MIN_LENGTH} символов с пробелами.")
        await state.clear()
        return

    if is_spam(user_id):
        await message.answer("Сообщение расценено как спам или флуд. Пожалуйста, дождитесь ручной проверки")
        await send_admin_notification(bot, user_id, name, text, post_id, session)
        ban_user(user_id)
        await state.clear()
        return

    if is_recent_post(user_id):
        await message.answer("Вы можете отправить только один пост каждые 10 минут.")
        await state.clear()
        return

    if contains_bad_words(text):
        await message.answer("Подозрение на запрещенные слова. Пожалуйста, дождитесь ручной проверки")
        await send_admin_notification(bot, user_id, name, text, post_id, session)
        ban_user(user_id)
        await state.clear()
        return

    if contains_forbidden_links(text):
        await message.answer("Подозрение на запрещенные ссылки. Пожалуйста, дождитесь ручной проверки")
        await send_admin_notification(bot, user_id, name, text, post_id, session)
        ban_user(user_id)
        await state.clear()
        return

    user_last_post_time[user_id] = datetime.datetime.now().timestamp()

    return True

def is_spam(user_id):
    if user_id not in user_message_count:
        user_message_count[user_id] = []
    current_time = datetime.datetime.now().timestamp()
    user_message_count[user_id] = [msg_time for msg_time in user_message_count[user_id] if current_time - msg_time < SPAM_PERIOD]

    user_message_count[user_id].append(current_time)
    if len(user_message_count[user_id]) > SPAM_LIMIT:
        return True
    return False

def is_recent_post(user_id):
    if user_id in user_last_post_time:
        current_time = datetime.datetime.now().timestamp()
        if current_time - user_last_post_time[user_id] < POST_LIMIT_PERIOD:
            return True
    return False

def is_valid_post(text):
    if len(text) < POST_MIN_LENGTH:
        return False

    if not re.search(r'\s', text) or re.match(r'^[\s\W]*$', text):
        return False
    return True

def ban_user(user_id):
    user_ban_list[user_id] = datetime.datetime.now() + datetime.timedelta(minutes=BAN_DURATION)

def is_user_banned(user_id):
    if user_id in user_ban_list:
        if datetime.datetime.now() < user_ban_list[user_id]:
            return True
        else:
            del user_ban_list[user_id]
    return False

async def send_admin_notification(
    bot: Bot,
    user_id: int,
    name: str,
    text: str,
    post_id: int,
    session: AsyncSession,
    photo_urls: List[str] = None,
    photo: str = None  
):
    photo_links = (photo_urls) if photo_urls else "Нет фотографий"

    notification_text = (
        f"Пользователь **{name}** ({user_id}) попытался отправить сообщение:\n\n\"{text}\"\n\n"
        f"Ссылки на фотографии:\n{photo_links}\n\n"
    )

    if photo:
        if not (photo.startswith('[') and photo.endswith(']')):
            photo = f'[{photo}]'
        
        try:
            photo_list = json.loads(photo)
        except json.JSONDecodeError:
            photo_list = []

        photo_str = json.dumps(photo_list)
    else:
        photo_str = "[]"

    await Gets.addGets(session, user_id, post_id, text, photo_str)

    await bot.send_message(
        ADMIN_CHAT_ID,
        notification_text,
        reply_markup=ban_markup(user_id=user_id, post_id=post_id)
    )
