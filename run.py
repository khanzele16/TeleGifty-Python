import asyncio
import logging

from bot import bot, dp
from app.handlers import router

from config import COMMANDS

async def main():
    dp.include_router(router)
    await bot.set_my_commands(COMMANDS)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())