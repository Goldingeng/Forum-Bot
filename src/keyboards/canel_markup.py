from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from .callback import *


def canel_markup(user_id: int):

    callback_canel = CanelCallback(user_id=user_id)
    
    inline_keyboard = [

        [
            InlineKeyboardButton(text="Отмена", callback_data=callback_canel.pack()),
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)