import asyncio
import logging

from aiogram.types import BotCommand

from config import Config
from tg_bot.db_models.db_gino import connect_to_db
from tg_bot.handlers import routers as routers_h
from tg_bot.handlers.start import cmd_start
from tg_bot.middlewares.access_restriction import AccRest
from tg_bot.misc.utils import Utils as Ut, global_variables

logger = logging.getLogger(__name__)


async def main():
    global_variables.update({"func_cmd_start": cmd_start})

    logging.getLogger("aiogram.event").setLevel(logging.WARNING)
    logging.basicConfig(level=logging.INFO,
                        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s')

    await connect_to_db(remove_data=Config.DATABASE_CLEANUP)
    await Ut.load_localizations_files()

    if routers_h:
        Config.DISPATCHER.include_routers(*routers_h)

    Config.DISPATCHER.message.outer_middleware(AccRest())

    bot_commands = [
        BotCommand(command="start", description="Начальное меню"),
    ]
    await Config.BOT.set_my_commands(commands=bot_commands)

    await Config.BOT.delete_webhook(drop_pending_updates=True)
    await Config.DISPATCHER.start_polling(Config.BOT, allowed_updates=Config.DISPATCHER.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
