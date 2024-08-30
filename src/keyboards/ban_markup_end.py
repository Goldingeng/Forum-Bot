from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from .callback import *


def ban_markup_end(user_id: int):

    callback_ban = BanCallback(user_id=user_id)
    
    inline_keyboard = [

        [
            InlineKeyboardButton(text="Бан", callback_data=callback_ban.pack()),
        ]
    ]


    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)