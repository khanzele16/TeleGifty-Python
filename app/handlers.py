import logging

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery

from aiogram.types import FSInputFile, CallbackQuery

from bot import bot

from app.keyboards import gift_keyboard
from app.session_slider import session_sliders, SessionSlider, get_or_create_session
from app.lib import prepare_gifts_data
from app.db import register_user, get_history, get_cart, add_to_cart, clean_cart, add_to_history
from app.keyboards import main_kb

router = Router()

# Команда start - запуск бота
@router.message(CommandStart())
async def command_start(message: Message):
    register_user(message)
    await message.answer(f'✨ Приветствую, {message.from_user.first_name}!\n\nЯ — искатель идеальных подарков, бот, который превращает заботы о подарках в магию.\n\n<b>Выбирай, покупай и радуй</b> — всё в одном месте! 🎁\n\n<blockquote>Если что-то непонятно, введите команду /help</blockquote>', parse_mode='HTML', reply_markup=main_kb.as_markup())

# Команда giftы - каталог подарков
@router.message(Command('gifts'))
async def command_gifts(message: Message):
    chat_id = message.chat.id
    session = session_sliders.get(chat_id) or SessionSlider(chat_id)
    session.current_page = 0
    session_sliders[chat_id] = session

    gifts = await prepare_gifts_data()
    if not gifts:
        await message.answer("🎁 Подарков пока нет.")
        return
    current_gift = gifts[0]
    sticker = FSInputFile(f"./stickers/{current_gift.id}.tgs")

    msg = await message.answer_sticker(sticker, reply_markup=gift_keyboard(
        gift=current_gift,
        current_page=0,
        total=len(gifts)
    ))

    session.last_message = msg

# Команда cart - корзина 
@router.message(Command('cart'))
async def command_cart(message: Message):
    user_id = message.from_user.id
    cart = get_cart(user_id)
    if not cart:
        await message.answer(
            "<b>🛒 Ваша корзина пуста.</b>\n\nДобавьте подарки, чтобы они здесь появились.\n\n<blockquote><b>TeleGifty</b> — ваш друг в мире подарков Telegram</blockquote>",
            parse_mode='HTML'
        )
        return
    text = "<b>🛒 Ваша корзина:</b>\n\n"
    for i, gift_ids in enumerate(cart, 1):
        gift_list = ", ".join(gift_ids) if isinstance(gift_ids, list) else str(gift_ids)
        text += f"{i}. 🎁 Подарки: <code>{gift_list}</code>\n"
    await message.answer(text, parse_mode='HTML')

# Команда gift - выбор подарка (выполняется только если есть id подарка)
@router.message(Command('gift'))
async def command_gift(message: Message):
    text = message.text
    full_text = text or ""
    parts = full_text.split(maxsplit=1)
    gift_id = parts[1] if len(parts) > 1 else None
    if not gift_id:
        await message.answer('<b>❓ Извините, я вас не понял!</b>\n\nВы не указали id подарка, к примеру:\n\n<code>/gift 1e3149dfg11d3r4t5</code>\n\n<blockquote><b>TeleGifty</b> — ваш друг в мире подарков Telegram</blockquote>', parse_mode='HTML')
    await message.answer(gift_id)

# Команда history - история покупок подарков
@router.message(Command('history'))
async def command_history(message: Message):
    history = get_history(message)
    if not history:
        await message.answer(
            "<b>История покупок</b>\n\n🕵️ У вас пока нет истории покупок.\n\n"
            "<blockquote><b>TeleGifty</b> — ваш друг в мире подарков Telegram</blockquote>",
            parse_mode="HTML"
        )
        return
    text = "📜 Ваша история покупок:\n\n"
    for i, (gift_id_str, sum_) in enumerate(history, 1):
        try:
            gift_ids = eval(gift_id_str) if isinstance(gift_id_str, str) else gift_id_str
            if not isinstance(gift_ids, list):
                gift_ids = [gift_ids]
        except Exception:
            gift_ids = [gift_id_str]
        ids_formatted = ", ".join(f"<code>{gid}</code>" for gid in gift_ids)
        text += f"{i}. 🎁 ID подарков: {ids_formatted} — {sum_} звёзд\n"
    await message.answer(text, parse_mode="HTML")

# Команда help - помощь
@router.message(Command('help'))
async def command_help(message: Message):
    await message.answer(f'<b>💭 Помощь </b>\n\nВ этом боте вы можете выбрать подарки, взять их в корзину и купить их в одном месте. Как один подарок, так и несколько подарков.\n\nПодарки покупаются с помощью <b>Telegram Stars.</b> Всё просто, даешь звезды — получаешь подарок.\n\n<i>Комиссия на подарки — 2%</i>\n\n<b>Команды и возможности</b>\n\n<code>/gift :id</code> — выбрать подарок\n<code>/gifts</code> — открыть каталог подарки\n<code>/history</code> — история покупок подарков\n<code>/cart</code> — корзина подаков\n<code>/help</code> — помощь\n\n<b>Связь с разработчиками бота</b>\n\n<i>Поддержка</i> — @khanzele и @frezanXpro\n\n<blockquote><b>TeleGifty</b> — ваш друг в мире подарков Telegram</blockquote>', parse_mode='HTML')

@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@router.message(lambda message: message.successful_payment is not None)
async def successful_payment_handler(message: Message):
    payment = message.successful_payment
    payload = payment.invoice_payload
    user_id = message.from_user.id
    try:
        if payload.startswith("gift:"):
            gift_id = payload.split(":")[-1]
            await bot.send_gift(chat_id=message.chat.id, gift_id=gift_id)
            add_to_history(user_id, [gift_id], payment.total_amount)

        elif payload.startswith("gifts:"):
            gift_ids = payload.split(":")[-1].split(",")
            for gift_id in gift_ids:
                await bot.send_gift(chat_id=message.chat.id, gift_id=gift_id)
            add_to_history(user_id, gift_ids, payment.total_amount)

        clean_cart(user_id)
    except Exception as e:
        logging.exception(f"Ошибка обработки успешной оплаты: {e}")

# Обработка всех остальных callback
@router.callback_query(lambda call: True)
async def callback_q(callback: CallbackQuery):
    data = callback.data
    chat_id = callback.message.chat.id
    session = get_or_create_session(chat_id)

    gifts = await prepare_gifts_data()

    if not session or not gifts:
        await callback.answer("❌ Сессия не найдена.")
        return

    if data.startswith("change_page:"):
        _, page_str = data.split(":")
        page = int(page_str)
        session.current_page = page

        current_gift = gifts[page]
        await callback.message.delete()
        sticker = FSInputFile(f"./stickers/{current_gift.id}.tgs")
        msg = await callback.message.answer_sticker(sticker, reply_markup=gift_keyboard(
            gift=current_gift,
            current_page=page,
            total=len(gifts)
        ))
        session.last_message = msg
        await callback.answer()

    elif data.startswith("buy_gift:"):
        gift_id = data.split(":")[1]
        gift = next((g for g in gifts if g.id == gift_id), None)
        if not gift:
            await callback.answer("❌ Подарок не найден.")
            return

        await callback.message.delete()
        await bot.send_invoice(
            chat_id=chat_id,
            title=f"🎁 Подарок {gift_id}",
            description=f"Подтвердите покупку подарка за {gift.star_count} ⭐",
            payload=f"gift:{gift_id}",
            provider_token="XTR",
            currency="XTR",
            prices=[{"label": "XTR", "amount": 1}],
        )
        await callback.answer()
    elif data.startswith("cart_gift:"):
        gift_id = data.split(":")[1]
        add_to_cart(callback.from_user.id, gift_id)
        logging.info(f"Добавляем подарок в корзину: user_id={callback.from_user.id}, gift_id={gift_id}")
        await callback.answer("🎁 Подарок добавлен в корзину!")
    elif data == "select_gift":
        await command_gifts(callback.message)
        await callback.answer()
    elif data == "card":
        await command_cart(callback.message)
        await callback.answer()
    else:
        await callback.answer("❔ Неизвестная команда")

# Обработка всех остальных сообщений
@router.message(F)
async def default_message(message: Message):
    await message.answer(f'<b>❓ Извините, я вас не понял!</b>\n\nЕсли хотите смоделировать правильный запрос, вы можете посмотреть команды в <b>/help</b>\n\n<blockquote><b>TeleGifty — ваш друг в мире подарков Telegram</b></blockquote>', parse_mode='HTML')