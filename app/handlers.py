import sqlite3

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from app.keyboards import main_kb

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    conn = sqlite3.connect('telegift.sql')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS users (id int primary key, username varchar(50), name varchar(50))')
    conn.commit()
    cur.execute(f'INSERT INTO users (id, username, name) VALUES ({message.from_user.id}, "{message.from_user.username}", "{message.from_user.first_name}")')
    cur.close()
    conn.close()
    await message.answer(f'✨ Приветствую, {message.from_user.first_name}!\n\nЯ — искатель идеальных подарков, бот, который превращает заботы о подарках в магию.\n\n<b>Выбирай, покупай и радуй</b> — всё в одном месте! 🎁', parse_mode='HTML', reply_markup=main_kb.as_markup())

@router.message(F)
async def photo(message: Message):
    await message.answer(f'<b>Извините!</b>\n\nЯ не понял что вы от меня хотите.\n\n<blockquote>Если хотите смоделировать правильный запрос, вы можете посмотреть команды в /help</blockquote>', parse_mode='HTML')