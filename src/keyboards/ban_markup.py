from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from .callback import *


def ban_markup(user_id: int, post_id : int):

    callback_ban = BanCallback(user_id=user_id)
    callback_skip = SkipCallback(user_id=user_id, post_id=post_id)
    
    inline_keyboard = [

        [
            InlineKeyboardButton(text="Бан", callback_data=callback_ban.pack()),
        ],
        [
            InlineKeyboardButton(text="Пропустить", callback_data=callback_skip.pack()),
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)