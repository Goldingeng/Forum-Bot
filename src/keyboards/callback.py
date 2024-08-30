from aiogram.filters.callback_data import CallbackData


class PostCallback(CallbackData, prefix="post"):
    user_id: int

class CanelCallback(CallbackData, prefix="canel"):
    user_id: int

class BanCallback(CallbackData, prefix="ban"):
    user_id: int

class UnBanCallback(CallbackData, prefix="unban"):
    user_id: int

class SkipCallback(CallbackData, prefix="skip"):
    user_id: int
    post_id: int