from aiogram import Router, F
from aiogram.types import Message

from src.keyboards import help_markup

help_router = Router(name="help")

@help_router.message(F.text.startswith("/start"))
async def help_handler(message: Message) -> None:
    await message.answer("/menu - отправить пост", parse_mode="HTML", reply_markup=help_markup())
