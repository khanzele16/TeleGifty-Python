from aiogram.types import BotCommand

TOKEN = '7210808707:AAHlipHm6iRGPydyl5fRkFlN0-L5rOlUGcU'

COMMANDS = [
    BotCommand(command='/start', description='Запустить бота'),
    BotCommand(command='/gift', description=':id Выбрать подарок'),
    BotCommand(command='/gifts', description='Каталог подарков'),
    BotCommand(command='/cart', description='Корзина подарков'),
    BotCommand(command='/history', description='История покупок'),
    BotCommand(command='/help', description='Помощь'),
]
