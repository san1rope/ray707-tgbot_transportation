import logging
from typing import Union

from aiogram import Router, F, types, enums
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from tg_bot.db_models.quick_commands import DbUser
from tg_bot.handlers.set_language import choose_language
from tg_bot.misc.utils import Utils as Ut

logger = logging.getLogger(__name__)
router = Router()


@router.message(F.chat.type == enums.ChatType.PRIVATE, CommandStart())
@router.callback_query(F.data == "rotate_to_start")
async def cmd_start(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
    uid = message.from_user.id
    await Ut.handler_log(logger, uid)
    await state.clear()

    if isinstance(message, types.CallbackQuery):
        await message.answer()

    db_user = await DbUser(tg_user_id=uid).select()
    if not db_user.language:
        return await choose_language(message=message, state=state, first_choose=True)

    text = await Ut.get_message_text(key="start_menu", lang=db_user.language)
    markup = await Ut.get_markup(mtype="inline", key="start_menu", lang=db_user.language)
    await Ut.send_step_message(user_id=uid, texts=[text], markups=[markup])
