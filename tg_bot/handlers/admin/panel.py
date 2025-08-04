import logging

from aiogram import Router, F, types, enums
from aiogram.filters import Command

from tg_bot.misc.utils import Utils as Ut

logger = logging.getLogger(__name__)
router = Router()


@router.message(F.chat.type == enums.ChatType.PRIVATE, Command("apanel"))
async def show_admin_panel(message: types.Message):
    uid = message.from_user.id
    await Ut.handler_log(logger, uid)
