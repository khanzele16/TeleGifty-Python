from app.handlers import command_start, command_gift, command_gifts, command_cart, command_history, command_help
from aiogram.types import BotCommand

TOKEN='7210808707:AAHlipHm6iRGPydyl5fRkFlN0-L5rOlUGcU'
COMMANDS=[
    BotCommand(command='/start', description='Запустить бота'),
    BotCommand(command='/gift', description=':id Выбрать подарок'),
    BotCommand(command='/gifts', description='Каталог подарков'),
    BotCommand(command='/cart', description='Корзина подарков'),
    BotCommand(command='/history', description='История покупок'),
    BotCommand(command='/help', description='Помощь')
]
COMMANDS_ACTIONS={
    '/start': command_start,
    '/gift': command_gift,
    '/gifts': command_gifts,
    '/cart': command_cart,
    '/history': command_history,
    '/help': command_help
}