import logging
from typing import Union

from aiogram import Router, F, types, enums
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from tg_bot.misc.utils import Utils as Ut

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "my_orders")
@router.message(F.chat.type == enums.ChatType.PRIVATE, Command("my_orders"))
async def cmd_my_orders(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
    uid = message.from_user.id
    await Ut.handler_log(logger, uid)

    if isinstance(message, types.CallbackQuery):
        await message.answer()
