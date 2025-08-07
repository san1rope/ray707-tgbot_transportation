import asyncio
import logging
from typing import Union

from aiogram import Router, F, types, enums
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import Config
from tg_bot.db_models.quick_commands import DbOrder, DbUser
from tg_bot.keyboards.inline import CustomInlineMarkups as Cim, CustomCallback
from tg_bot.misc.models import OrderForm
from tg_bot.misc.utils import Utils as Ut, global_variables, AdditionalButtons, localization

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "my_orders")
@router.message(F.chat.type == enums.ChatType.PRIVATE, Command("my_orders"))
async def cmd_my_orders(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
    uid = message.from_user.id
    await Ut.handler_log(logger, uid)

    if isinstance(message, types.CallbackQuery):
        await message.answer()

    db_user = await DbUser(tg_user_id=uid).select()

    db_orders = await DbOrder(tg_user_id=uid, status=0).select()
    if not db_orders:
        text = await Ut.get_message_text(key="my_order_list_is_empty", lang=db_user.language)
        await Ut.send_step_message(user_id=uid, texts=[text])
        await asyncio.sleep(1.5)
        return await global_variables["func_cmd_start"](message=message, state=state)

    text_title = await Ut.get_message_text(key="my_order_list_title", lang=db_user.language)
    additional_buttons = [AdditionalButtons(buttons={"rotate_to_start": None})]
    markup = await Ut.get_markup(lang=db_user.language, mtype="inline", additional_buttons=additional_buttons)
    await Ut.send_step_message(user_id=uid, texts=[text_title], markups=[markup])

    lang_data = localization[db_user.language] if localization.get(db_user.language) \
        else localization[Config.DEFAULT_LANG]
    status_list = lang_data["misc"]["order_status"]

    for order in db_orders:
        text = await Ut.get_message_text(key="my_order_list_order_text", lang=db_user.language)
        text = text.replace("%order_id%", str(order.id))
        text = text.replace("%order_status%", status_list[str(order.status)])
        text = text.replace("%order_form%", await OrderForm().form_completion(lang=db_user.language, db_model=order))

        markup = await Cim.cancel_my_order(lang=db_user.language, order_id=str(order.id))

        msg = await message.message.answer(text=text, reply_markup=markup, disable_web_page_preview=True)
        await Ut.add_msg_to_delete(user_id=uid, msg_id=msg.message_id)


@router.callback_query(CustomCallback.filter(F.role == "cancel_my_order"))
async def cancel_my_order(callback: types.CallbackQuery, callback_data: CustomCallback):
    await callback.answer()
    uid = callback.from_user.id
    await Ut.handler_log(logger, uid)

    db_user = await DbUser(tg_user_id=uid).select()

    text = await Ut.get_message_text(key="cancel_my_order_confirmation", lang=db_user.language)
    text = text.replace("%order_id%", str(callback_data.data))

    markup = await Cim.cancel_order_confirmation(lang=db_user.language, order_id=callback_data.data)
    await callback.message.edit_text(text=text, reply_markup=markup, disable_web_page_preview=True)


@router.callback_query(CustomCallback.filter(F.role == "cancel_my_order_confirm"))
async def cancel_my_order_confirm(callback: types.CallbackQuery, callback_data: CustomCallback):
    await callback.answer()
    uid = callback.from_user.id
    await Ut.handler_log(logger, uid)

    db_user = await DbUser(tg_user_id=uid).select()
    await DbOrder(db_id=int(callback_data.data)).update(status=3)

    text = await Ut.get_message_text(key="cancel_my_order_confirm", lang=db_user.language)
    text = text.replace("%order_id%", callback_data.data)
    await callback.message.edit_text(text=text, disable_web_page_preview=True)


@router.callback_query(CustomCallback.filter(F.role == "cancel_my_order_back"))
async def cancel_my_order_back(callback: types.CallbackQuery, callback_data: CustomCallback):
    await callback.answer()
    uid = callback.from_user.id
    await Ut.handler_log(logger, uid)

    db_user = await DbUser(tg_user_id=uid).select()
    order = await DbOrder(db_id=int(callback_data.data)).select()

    lang_data = localization[db_user.language] if localization.get(db_user.language) \
        else localization[Config.DEFAULT_LANG]
    status_list = lang_data["misc"]["order_status"]

    text = await Ut.get_message_text(key="my_order_list_order_text", lang=db_user.language)
    text = text.replace("%order_id%", str(order.id))
    text = text.replace("%order_status%", status_list[str(order.status)])
    text = text.replace("%order_form%", await OrderForm().form_completion(lang=db_user.language, db_model=order))

    markup = await Cim.cancel_my_order(lang=db_user.language, order_id=str(order.id))

    await callback.message.edit_text(text=text, reply_markup=markup, disable_web_page_preview=True)
