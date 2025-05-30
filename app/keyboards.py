from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

main_kb = InlineKeyboardBuilder()

main_kb.row(
    InlineKeyboardButton(
        text='🎁 Выбрать подарки',
        callback_data='select_gift'
    )
).row(
    InlineKeyboardButton(
        text='🛒 Корзина',
        callback_data='card'
    )
)