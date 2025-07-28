import asyncio
import logging

from aiogram.types import BotCommand

from config import Config
from tg_bot.db_models.db_gino import connect_to_db
from tg_bot.handlers import routers

logger = logging.getLogger(__name__)


async def main():
    logging.getLogger("aiogram.event").setLevel(logging.WARNING)
    logging.basicConfig(level=logging.INFO,
                        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s')

    await connect_to_db(remove_data=Config.DATABASE_CLEANUP)

    if routers:
        Config.DISPATCHER.include_routers(*routers)

    bot_commands = [
        BotCommand(command="start", description="Начальное меню"),
    ]
    await Config.BOT.set_my_commands(commands=bot_commands)


if __name__ == "__main__":
    asyncio.run(main())
