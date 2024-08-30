import asyncio
from aiogram import Bot, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
from typing import List
from ..keyboards import ban_markup_end
from ..config import channel_id, adminpub
scheduler = AsyncIOScheduler()
last_post_time = None


async def schedule_post(bot: Bot, message: str, user_id: int, post_time: datetime):
    try:
        now = datetime.now()
        if post_time > now:
            delay = (post_time - now).total_seconds()
            print(f"Пост будет отправлен через {delay} секунд. Текущее время: {now}.")
            await asyncio.sleep(delay)
        
        await bot.send_message(chat_id=channel_id, text=message)
        await bot.send_message(chat_id=adminpub, text=message, reply_markup=ban_markup_end(user_id))
        global last_post_time
        last_post_time = datetime.now()
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")

async def send_scheduled_post(bot: Bot, message: str, user_id: int):
    global last_post_time
    try:
        now = datetime.now()
        if last_post_time:
            time_since_last_post = now - last_post_time
            delay = timedelta(minutes=0.1) - time_since_last_post
            if delay > timedelta(seconds=0):
                post_time = now + delay
            else:
                post_time = now
        else:
            post_time = now
        
        scheduler.add_job(schedule_post, trigger=DateTrigger(run_date=post_time),
                          args=[bot, message, user_id, post_time])
        print(f"Запланирован пост на {post_time}.")
        
        scheduler.start()
    except Exception as e:
        print(f"Ошибка при планировании сообщения: {e}")

async def send_scheduled_post_media(bot: Bot, user_id: int, media: List[str] = None):
    global last_post_time
    try:
        now = datetime.now()
        if last_post_time:
            time_since_last_post = now - last_post_time
            delay = timedelta(minutes=10) - time_since_last_post
            if delay > timedelta(seconds=0):
                post_time = now + delay
            else:
                post_time = now
        else:
            post_time = now
        
        scheduler.add_job(schedule_post_media, trigger=DateTrigger(run_date=post_time),
                          args=[bot, user_id, media, post_time])
        print(f"Запланировано групповое изображение на {post_time}.")
        
        scheduler.start()
    except Exception as e:
        print(f"Ошибка при планировании группового изображения: {e}")

async def schedule_post_media(bot: Bot, user_id: int, media: List[str], post_time: datetime):
    try:
        now = datetime.now()
        if post_time > now:
            delay = (post_time - now).total_seconds()
            print(f"Групповое изображение будет отправлено через {delay} секунд. Текущее время: {now}.")
            await asyncio.sleep(delay)
        
        await bot.send_media_group(chat_id=channel_id, media=media)
        await bot.send_message(chat_id=adminpub, text=f"Групповое изображение от {user_id}", reply_markup=ban_markup_end(user_id))
        global last_post_time
        last_post_time = datetime.now()
    except Exception as e:
        print(f"Ошибка при отправке группового изображения: {e}")
