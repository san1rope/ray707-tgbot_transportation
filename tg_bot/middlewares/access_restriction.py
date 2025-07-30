import logging
from typing import Dict, Any, Callable, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from tg_bot.db_models.quick_commands import DbUser

logger = logging.getLogger(__name__)


class AccRest(BaseMiddleware):
    def __init__(self):
        pass

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ):
        uid = event.from_user.id

        db_user = await DbUser(tg_user_id=uid).select()
        if db_user:
            return await handler(event, data)
