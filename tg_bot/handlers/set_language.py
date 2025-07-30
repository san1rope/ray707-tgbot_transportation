import asyncio
import logging
from typing import Union, Optional

from aiogram import Router, F, types, enums
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import Config
from tg_bot.db_models.quick_commands import DbUser
from tg_bot.misc.states import SetLanguage
from tg_bot.misc.utils import Utils as Ut, global_variables

logger = logging.getLogger(__name__)
router = Router()


@router.message(F.chat.type == enums.ChatType.PRIVATE, Command("language"))
@router.callback_query(F.data == "choose_language")
async def choose_language(message: Union[types.Message, types.CallbackQuery], state: FSMContext,
                          first_choose: bool = False):
    uid = message.from_user.id
    await Ut.handler_log(logger, uid)

    if isinstance(message, types.CallbackQuery):
        await message.answer()

    if first_choose:
        ulang = Config.DEFAULT_LANG

    else:
        db_user = await DbUser(tg_user_id=uid).select()
        ulang = db_user.language

    text = await Ut.get_message_text(key="choose_lang", lang=ulang)
    markup = await Ut.get_markup(mtype="inline", key="choose_lang", lang=ulang)
    await Ut.send_step_message(user_id=uid, texts=[text], markups=[markup])

    await state.set_state(SetLanguage.ChooseLanguage)


@router.callback_query(SetLanguage.ChooseLanguage)
async def language_is_selected(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    uid = callback.from_user.id
    await Ut.handler_log(logger, uid)

    await DbUser(tg_user_id=uid).update(language=callback.data)

    text = await Ut.get_message_text(key="language_has_been_changed", lang=callback.data)
    await Ut.send_step_message(user_id=uid, texts=[text])
    await asyncio.sleep(1.5)

    await global_variables["func_cmd_start"](message=callback, state=state)
