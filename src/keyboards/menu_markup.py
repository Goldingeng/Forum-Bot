from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from .callback import *


def menu_markup(user_id: int):

    callback_post = PostCallback(user_id=user_id)
    
    inline_keyboard = [
        [
            InlineKeyboardButton(text="Написать пост", callback_data=callback_post.pack()),
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)