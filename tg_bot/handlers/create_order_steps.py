import logging
from datetime import datetime
from typing import Optional, Union

from aiogram.fsm.context import FSMContext
from aiogram import Router, F, types, enums

from config import Config
from tg_bot.db_models.quick_commands import DbUser
from tg_bot.db_models.schemas import Order
from tg_bot.keyboards.default import request_contact_default
from tg_bot.keyboards.inline import CustomInlineMarkups as Cim
from tg_bot.misc.models import OrderForm
from tg_bot.misc.states import CreateOrder
from tg_bot.misc.utils import Utils as Ut, AdditionalButtons

logger = logging.getLogger(__name__)
router = Router()


class OrderCreationSteps:

    @staticmethod
    async def model_form_correct(lang: str, data_model: Optional[Union[OrderForm, Order]] = None) -> str:
        if isinstance(data_model, OrderForm):
            title = await data_model.form_completion(lang=lang)

        elif isinstance(data_model, Order):
            title = await OrderForm().form_completion(lang=lang, db_model=data_model)

        else:
            title = ""

        return title

    @classmethod
    async def name(cls, state: FSMContext, lang: str, data_model: Optional[Union[OrderForm, Order]] = None):
        text_question = await Ut.get_message_text(key="order_create_write_name", lang=lang)
        text_form = await cls.model_form_correct(lang=lang, data_model=data_model)

        await Ut.send_step_message(user_id=state.key.user_id, texts=[text_form, text_question])
        await state.set_state(CreateOrder.WriteName)

    @classmethod
    async def name_handler(cls, message: Union[types.Message, types.CallbackQuery], state: FSMContext):
        uid = message.from_user.id
        await Ut.handler_log(logger, uid)

        if isinstance(message, types.CallbackQuery):
            await message.answer()

            return

        db_user = await DbUser(tg_user_id=uid).select()
        name = message.text.strip()
        if len(name) < 4:
            text = await Ut.get_message_text(key="wrong_name_format", lang=db_user.language)
            msg = await message.answer(text=text)
            return await Ut.add_msg_to_delete(user_id=uid, msg_id=msg.message_id)

        data = await state.get_data()
        await data["call_function"](state=state, returned_data=name)

    @classmethod
    async def phone(cls, state: FSMContext, lang: str, data_model: Optional[Union[OrderForm, Order]] = None):
        text_question = await Ut.get_message_text(key="order_create_write_phone", lang=lang)
        text_form = await cls.model_form_correct(lang=lang, data_model=data_model)
        await Ut.send_step_message(user_id=state.key.user_id, texts=[text_form, text_question])

        text_question = await Ut.get_message_text(key="order_create_request_contact", lang=lang)
        msg = await Config.BOT.send_message(chat_id=state.key.user_id, text=text_question,
                                            reply_markup=await request_contact_default(lang=lang))
        await Ut.add_msg_to_delete(user_id=state.key.user_id, msg_id=msg.message_id)

        await state.set_state(CreateOrder.WritePhone)

    @classmethod
    async def phone_handler(cls, message: [types.Message, types.CallbackQuery], state: FSMContext):
        uid = message.from_user.id
        await Ut.handler_log(logger, uid)

        if isinstance(message, types.CallbackQuery):
            await message.answer()

            return

        if message.contact:
            phone_number = message.contact.phone_number.replace("+", "")

        else:
            db_user = await DbUser(tg_user_id=uid).select()

            phone_number = message.text.strip().replace("+", "")
            if not phone_number.isdigit():
                text = await Ut.get_message_text(key="wrong_phone_number_format", lang=db_user.language)
                msg = await message.answer(text=text)
                return await Ut.add_msg_to_delete(user_id=uid, msg_id=msg.message_id)

            if not (10 <= len(phone_number) <= 15):
                text = await Ut.get_message_text(key="phone_number_range_limit", lang=db_user.language)
                msg = await message.answer(text=text)
                return await Ut.add_msg_to_delete(user_id=uid, msg_id=msg.message_id)

        data = await state.get_data()
        await data["call_function"](state=state, returned_data=phone_number)

    @classmethod
    async def address(cls, state: FSMContext, lang: str, data_model: Optional[Union[OrderForm, Order]] = None):
        text_question = await Ut.get_message_text(key="order_create_write_address", lang=lang)
        text_form = await cls.model_form_correct(lang=lang, data_model=data_model)

        await Ut.send_step_message(user_id=state.key.user_id, texts=[text_form, text_question])
        await state.set_state(CreateOrder.WriteAddress)

    @classmethod
    async def address_handler(cls, message: [types.Message, types.CallbackQuery], state: FSMContext):
        uid = message.from_user.id
        await Ut.handler_log(logger, uid)

        if isinstance(message, types.CallbackQuery):
            await message.answer()

            return

        db_user = await DbUser(tg_user_id=uid).select()
        address = message.text.strip()
        if len(address) < 10:
            text = await Ut.get_message_text(key="wrong_address_format", lang=db_user.language)
            msg = await message.answer(text=text)
            return await Ut.add_msg_to_delete(user_id=uid, msg_id=msg.message_id)

        data = await state.get_data()
        await data["call_function"](state=state, returned_data=address)

    @classmethod
    async def description(cls, state: FSMContext, lang: str, data_model: Optional[Union[OrderForm, Order]] = None):
        text_question = await Ut.get_message_text(key="order_create_write_description", lang=lang)
        text_form = await cls.model_form_correct(lang=lang, data_model=data_model)

        await Ut.send_step_message(user_id=state.key.user_id, texts=[text_form, text_question])
        await state.set_state(CreateOrder.WriteDescription)

    @classmethod
    async def description_handler(cls, message: [types.Message, types.CallbackQuery], state: FSMContext):
        uid = message.from_user.id
        await Ut.handler_log(logger, uid)

        if isinstance(message, types.CallbackQuery):
            await message.answer()

            return

        db_user = await DbUser(tg_user_id=uid).select()
        description = message.text.strip()
        if len(description) < 10:
            text = await Ut.get_message_text(key="wrong_description_format", lang=db_user.language)
            msg = await message.answer(text=text)
            return await Ut.add_msg_to_delete(user_id=uid, msg_id=msg.message_id)

        data = await state.get_data()
        await data["call_function"](state=state, returned_data=description)

    @classmethod
    async def weight(cls, state: FSMContext, lang: str, data_model: Optional[Union[OrderForm, Order]] = None):
        text_question = await Ut.get_message_text(key="order_create_write_weight", lang=lang)
        text_form = await cls.model_form_correct(lang=lang, data_model=data_model)

        await Ut.send_step_message(user_id=state.key.user_id, texts=[text_form, text_question])
        await state.set_state(CreateOrder.WriteWeight)

    @classmethod
    async def weight_handler(cls, message: [types.Message, types.CallbackQuery], state: FSMContext):
        uid = message.from_user.id
        await Ut.handler_log(logger, uid)

        if isinstance(message, types.CallbackQuery):
            await message.answer()

            return

        weight = message.text.strip()

        data = await state.get_data()
        await data["call_function"](state=state, returned_data=weight)

    @classmethod
    async def pallets(cls, state: FSMContext, lang: str, data_model: Optional[Union[OrderForm, Order]] = None):
        text_question = await Ut.get_message_text(key="order_create_write_number_of_pallets", lang=lang)
        text_form = await cls.model_form_correct(lang=lang, data_model=data_model)

        await Ut.send_step_message(user_id=state.key.user_id, texts=[text_form, text_question])
        await state.set_state(CreateOrder.WritePallets)

    @classmethod
    async def pallets_handler(cls, message: [types.Message, types.CallbackQuery], state: FSMContext):
        uid = message.from_user.id
        await Ut.handler_log(logger, uid)

        db_user = await DbUser(tg_user_id=uid).select()
        number_of_pallets = message.text.strip()
        if not number_of_pallets.isdigit():
            text = await Ut.get_message_text(key="wrong_number_of_pallets_format", lang=db_user.language)
            msg = await message.answer(text=text)
            return await Ut.add_msg_to_delete(user_id=uid, msg_id=msg.message_id)

        data = await state.get_data()
        await data["call_function"](state=state, returned_data=number_of_pallets)

    @classmethod
    async def delivery_time_date(cls, state: FSMContext, lang: str,
                                 data_model: Optional[Union[OrderForm, Order]] = None):
        text_question = await Ut.get_message_text(key="order_create_choose_delivery_time_date", lang=lang)
        markup = await Cim.calendar(date_time=datetime.now(tz=Config.TIMEZONE), lang=lang)

        text_form = await cls.model_form_correct(lang=lang, data_model=data_model)

        await Ut.send_step_message(user_id=state.key.user_id, texts=[text_form, text_question], markups=[None, markup])
        await state.set_state(CreateOrder.WriteDeliveryTimeDate)

    @classmethod
    async def delivery_time_date_handler(cls, callback: types.CallbackQuery, state: FSMContext):
        await callback.answer()
        uid = callback.from_user.id
        await Ut.handler_log(logger, uid)

        db_user = await DbUser(tg_user_id=uid).select()

        cd = callback.data
        if "l:" in cd:
            date_time = datetime.strptime(cd.replace("l:", ""), "%d.%m.%Y")
            current_dt = datetime.now(tz=Config.TIMEZONE)
            if current_dt.year == date_time.year and current_dt.month == date_time.month:
                date_time = current_dt

            return await callback.message.edit_reply_markup(
                reply_markup=await Cim.calendar(date_time=date_time, lang=db_user.language))

        elif "r:" in cd:
            date_time = datetime.strptime(cd.replace("r:", ""), "%d.%m.%Y")
            return await callback.message.edit_reply_markup(
                reply_markup=await Cim.calendar(date_time=date_time, lang=db_user.language))

        elif "." in cd:
            returned_value = datetime.strptime(cd, "%d.%m.%Y")

            data = await state.get_data()
            await data["call_function"](state=state, returned_data=returned_value)

    @classmethod
    async def delivery_time_hours(cls, state: FSMContext, lang: str,
                                  data_model: Optional[Union[OrderForm, Order]] = None):
        text_question = await Ut.get_message_text(key="order_create_choose_delivery_time_hours", lang=lang)
        text_form = await cls.model_form_correct(lang=lang, data_model=data_model)

        await Ut.send_step_message(user_id=state.key.user_id, texts=[text_form, text_question])
        await state.set_state(CreateOrder.WriteDeliveryTimeHours)

    @classmethod
    async def delivery_time_hours_handler(cls, message: Union[types.Message, types.CallbackQuery], state: FSMContext):
        uid = message.from_user.id
        await Ut.handler_log(logger, uid)

        if isinstance(message, types.CallbackQuery):
            await message.answer()

            return

        db_user = await DbUser(tg_user_id=uid).select()
        hours = message.text.strip()

        try:
            datetime.strptime(f"10.10.2024 {hours}", "%d.%m.%Y %H:%M")

        except ValueError:
            text = await Ut.get_message_text(key="wrong_hours_format", lang=db_user.language)
            msg = await message.answer(text=text)
            return await Ut.add_msg_to_delete(user_id=uid, msg_id=msg.message_id)

        data = await state.get_data()
        await data["call_function"](state=state, returned_data=hours)

    @classmethod
    async def comment(cls, state: FSMContext, lang: str, data_model: Optional[Union[OrderForm, Order]] = None):
        text_question = await Ut.get_message_text(key="order_create_write_comment", lang=lang)
        additional_buttons = [AdditionalButtons(buttons={"skip": None})]
        markup = await Ut.get_markup(lang=lang, mtype="inline", additional_buttons=additional_buttons)

        text_form = await cls.model_form_correct(lang=lang, data_model=data_model)

        await Ut.send_step_message(user_id=state.key.user_id, texts=[text_form, text_question], markups=[None, markup])
        await state.set_state(CreateOrder.WriteComment)

    @classmethod
    async def comment_handler(cls, message: [types.Message, types.CallbackQuery], state: FSMContext):
        uid = message.from_user.id
        await Ut.handler_log(logger, uid)

        if isinstance(message, types.CallbackQuery):
            await message.answer()

            if message.data == "skip":
                comment = None

            else:
                return

        else:
            comment = message.text.strip()

        data = await state.get_data()
        await data["call_function"](state=state, returned_data=comment)


router.message.register(OrderCreationSteps.name_handler, CreateOrder.WriteName)
router.callback_query.register(OrderCreationSteps.name_handler, CreateOrder.WriteName)
router.message.register(OrderCreationSteps.phone_handler, CreateOrder.WritePhone)
router.callback_query.register(OrderCreationSteps.phone_handler, CreateOrder.WritePhone)
router.message.register(OrderCreationSteps.address_handler, CreateOrder.WriteAddress)
router.callback_query.register(OrderCreationSteps.address_handler, CreateOrder.WriteAddress)
router.message.register(OrderCreationSteps.description_handler, CreateOrder.WriteDescription)
router.callback_query.register(OrderCreationSteps.description_handler, CreateOrder.WriteDescription)
router.message.register(OrderCreationSteps.weight_handler, CreateOrder.WriteWeight)
router.callback_query.register(OrderCreationSteps.weight_handler, CreateOrder.WriteWeight)
router.message.register(OrderCreationSteps.pallets_handler, CreateOrder.WritePallets)
router.callback_query.register(OrderCreationSteps.pallets_handler, CreateOrder.WritePallets)
router.callback_query.register(OrderCreationSteps.delivery_time_date_handler, CreateOrder.WriteDeliveryTimeDate)
router.message.register(OrderCreationSteps.delivery_time_hours_handler, CreateOrder.WriteDeliveryTimeHours)
router.callback_query.register(OrderCreationSteps.delivery_time_hours_handler, CreateOrder.WriteDeliveryTimeHours)
router.message.register(OrderCreationSteps.comment_handler, CreateOrder.WriteComment)
router.callback_query.register(OrderCreationSteps.comment_handler, CreateOrder.WriteComment)
