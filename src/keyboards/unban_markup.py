from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from .callback import *


def unban_markup(user_id: int):

    callback_unban = UnBanCallback(user_id=user_id)
    
    inline_keyboard = [

        [
            InlineKeyboardButton(text="Разбан", callback_data=callback_unban.pack()),
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)