import logging

from aiogram import Router, F, types, enums
from aiogram.filters import CommandStart

from tg_bot.misc.utils import Utils as Ut

logger = logging.getLogger(__name__)
router = Router()


@router.message(F.chat.type == enums.ChatType.PRIVATE, CommandStart())
async def cmd_start(message: types.Message):
    uid = message.from_user.id
    await Ut.handler_log(logger, uid)
