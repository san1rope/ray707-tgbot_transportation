import asyncio
import logging
from typing import Union

from aiogram import Router, F, types, enums
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from tg_bot.db_models.quick_commands import DbUser, DbOrder
from tg_bot.handlers.create_order_steps import OrderCreationSteps
from tg_bot.misc.models import OrderForm
from tg_bot.misc.states import CreateOrder
from tg_bot.misc.utils import Utils as Ut, global_variables, AdditionalButtons, call_functions

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "create_order")
@router.message(F.chat.type == enums.ChatType.PRIVATE, Command("create_order"))
async def write_name(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
    uid = message.from_user.id
    await Ut.handler_log(logger, uid)

    if isinstance(message, types.CallbackQuery):
        await message.answer()

    db_user = await DbUser(tg_user_id=uid).select()

    order_model = OrderForm()
    await state.update_data(order_model=order_model, call_function=write_phone)

    await OrderCreationSteps().name(state=state, lang=db_user.language, data_model=order_model)


async def write_phone(state: FSMContext, returned_data: Union[str, int]):
    data = await state.get_data()
    order_model: OrderForm = data["order_model"]

    order_model.name = returned_data
    await state.update_data(order_model=order_model, call_function=write_address)

    db_user = await DbUser(tg_user_id=state.key.user_id).select()
    await OrderCreationSteps().phone(state=state, data_model=order_model, lang=db_user.language)


async def write_address(state: FSMContext, returned_data: Union[str, int]):
    data = await state.get_data()
    order_model: OrderForm = data["order_model"]

    order_model.phone = returned_data
    await state.update_data(order_model=order_model, call_function=write_description)

    db_user = await DbUser(tg_user_id=state.key.user_id).select()
    await OrderCreationSteps().address(state=state, data_model=order_model, lang=db_user.language)


async def write_description(state: FSMContext, returned_data: Union[str, int]):
    data = await state.get_data()
    order_model: OrderForm = data["order_model"]

    order_model.address = returned_data
    await state.update_data(order_model=order_model, call_function=write_weight)

    db_user = await DbUser(tg_user_id=state.key.user_id).select()
    await OrderCreationSteps().description(state=state, data_model=order_model, lang=db_user.language)


async def write_weight(state: FSMContext, returned_data: Union[str, int]):
    data = await state.get_data()
    order_model: OrderForm = data["order_model"]

    order_model.description = returned_data
    await state.update_data(order_model=order_model, call_function=write_number_of_pallets)

    db_user = await DbUser(tg_user_id=state.key.user_id).select()
    await OrderCreationSteps().weight(state=state, data_model=order_model, lang=db_user.language)


async def write_number_of_pallets(state: FSMContext, returned_data: Union[str, int]):
    data = await state.get_data()
    order_model: OrderForm = data["order_model"]

    order_model.weight = returned_data
    await state.update_data(order_model=order_model, call_function=choose_delivery_time_date)

    db_user = await DbUser(tg_user_id=state.key.user_id).select()
    await OrderCreationSteps().pallets(state=state, data_model=order_model, lang=db_user.language)


async def choose_delivery_time_date(state: FSMContext, returned_data: Union[str, int]):
    data = await state.get_data()
    order_model: OrderForm = data["order_model"]

    order_model.pallets = returned_data
    await state.update_data(order_model=order_model, call_function=choose_delivery_time_hours)

    db_user = await DbUser(tg_user_id=state.key.user_id).select()
    await OrderCreationSteps().delivery_time_date(state=state, data_model=order_model, lang=db_user.language)


async def choose_delivery_time_hours(state: FSMContext, returned_data: Union[str, int]):
    data = await state.get_data()
    order_model: OrderForm = data["order_model"]

    order_model.delivery_time = returned_data
    await state.update_data(order_model=order_model, call_function=write_comment)

    db_user = await DbUser(tg_user_id=state.key.user_id).select()
    await OrderCreationSteps().delivery_time_hours(state=state, data_model=order_model, lang=db_user.language)


async def write_comment(state: FSMContext, returned_data: Union[str, int]):
    data = await state.get_data()
    order_model: OrderForm = data["order_model"]

    hours, minutes = returned_data.split(":")
    order_model.delivery_time = order_model.delivery_time.replace(hour=int(hours), minute=int(minutes))
    await state.update_data(order_model=order_model, call_function=form_confirmation)

    db_user = await DbUser(tg_user_id=state.key.user_id).select()
    await OrderCreationSteps().comment(state=state, data_model=order_model, lang=db_user.language)


async def form_confirmation(state: FSMContext, returned_data: Union[str, int]):
    db_user = await DbUser(tg_user_id=state.key.user_id).select()
    data = await state.get_data()
    order_model: OrderForm = data["order_model"]

    order_model.comment = returned_data
    await state.update_data(order_model=order_model)

    text_question = await Ut.get_message_text(key="order_create_confirmation", lang=db_user.language)
    text_form = await order_model.form_completion(lang=db_user.language)

    additional_buttons = [AdditionalButtons(buttons={"back": None})]
    markup = await Ut.get_markup(mtype="inline", key="confirmation", lang=db_user.language,
                                 additional_buttons=additional_buttons)
    await Ut.send_step_message(user_id=state.key.user_id, texts=[text_form, text_question], markups=[None, markup])

    await state.set_state(CreateOrder.FormConfirmation)


@router.callback_query(CreateOrder.FormConfirmation)
async def create_finish(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    uid = callback.from_user.id
    await Ut.handler_log(logger, uid)

    db_user = await DbUser(tg_user_id=uid).select()
    data = await state.get_data()
    order_model: OrderForm = data["order_model"]

    cd = callback.data

    if cd == "confirm":
        result = await DbOrder(tg_user_id=uid, status=0, **(order_model.model_dump())).add()

        if result:
            text = await Ut.get_message_text(key="order_create_finish", lang=db_user.language)
            await Ut.send_step_message(user_id=uid, texts=[text])
            await state.clear()

        else:
            text = await Ut.get_message_text(key="order_create_finish_error", lang=db_user.language)
            msg = await callback.message.answer(text=text)
            await Ut.add_msg_to_delete(user_id=uid, msg_id=msg.message_id)

        await asyncio.sleep(2)
        await global_variables["func_cmd_start"](message=callback, state=state)

    elif cd == "back":
        order_model.comment = None
        await state.update_data(order_model=order_model, call_function=form_confirmation)

        return await OrderCreationSteps().comment(state=state, data_model=order_model, lang=db_user.language)


call_functions.update({
    "name": write_name, "phone": write_phone, "address": write_address, "description": write_description,
    "weight": write_weight, "pallets": write_number_of_pallets, "delivery_time_date": choose_delivery_time_date,
    "delivery_time_hours": choose_delivery_time_hours, "comment": write_comment
})
