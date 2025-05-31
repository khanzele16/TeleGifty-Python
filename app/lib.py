from pathlib import Path
from aiogram.types import Message
from aiohttp import ClientSession
from bot import bot

stickers_dir = Path("./stickers")
stickers_dir.mkdir(exist_ok=True)

def sticker_is_downloaded(sticker_filename: str) -> bool:
    file_path = stickers_dir / sticker_filename
    return file_path.exists()

async def download_sticker(gift_id: str, file_id: str) -> None:
    file = await bot.get_file(file_id)
    file_path = file.file_path
    url = f"https://api.telegram.org/file/bot{bot.token}/{file_path}"
    save_path = stickers_dir / f"{gift_id}.tgs"

    async with ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200 or response.content_length == 0:
                raise Exception(
                    f"Failed to download sticker {gift_id}: status {response.status}, length {response.content_length}"
                )
            content = await response.read()
            if not content:
                raise Exception("Downloaded file is empty")
            with open(save_path, "wb") as f:
                f.write(content)

async def prepare_gifts_data():
    try:
        gifts = await bot.get_available_gifts()
        for gift in gifts.gifts:
            sticker = gift.sticker
            gift_id = gift.id
            file_id = sticker.file_id
            if not sticker_is_downloaded(f"{gift_id}.tgs"):
                await download_sticker(gift_id, file_id)
        return gifts.gifts
    except Exception as err:
        print(f"⚠️ Error while processing gifts: {err}")