import asyncio
import logging
from typing import Union

from aiogram import Router, F, types, enums
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from tg_bot.db_models.quick_commands import DbOrder, DbUser
from tg_bot.misc.utils import Utils as Ut, global_variables, AdditionalButtons

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "my_orders")
@router.message(F.chat.type == enums.ChatType.PRIVATE, Command("my_orders"))
async def cmd_my_orders(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
    uid = message.from_user.id
    await Ut.handler_log(logger, uid)

    if isinstance(message, types.CallbackQuery):
        await message.answer()
        message = message.message

    db_user = await DbUser(tg_user_id=uid).select()

    db_orders = await DbOrder(tg_user_id=uid).select()
    if not db_orders:
        text = await Ut.get_message_text(key="my_order_list_is_empty", lang=db_user.language)
        await Ut.send_step_message(user_id=uid, texts=[text])
        await asyncio.sleep(1.5)
        return await global_variables["func_cmd_start"](message=message, state=state)

    text_title = await Ut.get_message_text(key="my_order_list_title", lang=db_user.language)
    additional_buttons = [AdditionalButtons(buttons={"rotate_to_start": None})]
    markup = await Ut.get_markup(lang=db_user.language, mtype="inline", additional_buttons=additional_buttons)
    await Ut.send_step_message(user_id=uid, texts=[text_title], markups=[markup])

    for order in db_orders:
        text = await Ut.get_message_text(key="my_order_list_order_text", lang=db_user.language)
        text = text.replace("%order_id%", str(order.id))
        text = text.replace("%order_status%", str(order.status))
        text = text.replace("%order_name%", order.name)
        text = text.replace("%order_phone%", order.phone)
        text = text.replace("%order_address%", order.address)
        text = text.replace("%order_description%", order.description)
        text = text.replace("%order_weight%", order.weight)
        text = text.replace("%order_pallets%", str(order.pallets))
        text = text.replace("%order_delivery_time%", order.delivery_time.strftime("%d.%m.%Y %H:%M"))
        text = text.replace("%order_comment%", order.comment if order.comment is not None else "")

        msg = await message.answer(text=text)
        await Ut.add_msg_to_delete(user_id=uid, msg_id=msg.message_id)
