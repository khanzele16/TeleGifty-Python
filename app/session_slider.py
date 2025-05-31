from typing import Optional
from aiogram.types import Message
from cachetools import TTLCache

class SessionSlider:
    def __init__(self, chat_id: int):
        self.chat_id = chat_id
        self.current_page = 0
        self.last_message: Optional[Message] = None

session_sliders: TTLCache[int, SessionSlider] = TTLCache(maxsize=10_000, ttl=3600)

def get_or_create_session(chat_id: int) -> SessionSlider:
    session = session_sliders.get(chat_id)
    if not session:
        session = SessionSlider(chat_id)
        session_sliders[chat_id] = session
    return session
