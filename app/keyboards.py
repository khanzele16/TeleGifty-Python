from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

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

def gift_keyboard(gift, current_page, total):
    navigation_row = []
    if current_page > 0:
        navigation_row.append(InlineKeyboardButton(
            text="⬅️",
            callback_data=f"change_page:{current_page - 1}"
        ))
    if current_page < total - 1:
        navigation_row.append(InlineKeyboardButton(
            text="➡️",
            callback_data=f"change_page:{current_page + 1}"
        ))
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"Купить за {gift.star_count} ⭐", callback_data=f"buy_gift:{gift.id}")],
            navigation_row if navigation_row else [],
            [InlineKeyboardButton(text="🛒 В корзину", callback_data=f"cart_gift:{gift.id}")]
        ]
    )