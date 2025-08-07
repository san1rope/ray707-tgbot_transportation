from datetime import datetime
from typing import Optional, List, Dict, Union

from aiogram.utils.markdown import hcode
from pydantic import BaseModel

from config import Config
from tg_bot.db_models.schemas import Order
from tg_bot.misc.utils import localization


class OrderForm(BaseModel):
    name: Optional[str] = None
    phone_manager: Optional[str] = None
    phone_receiver: Optional[str] = None
    address: Optional[str] = None
    body_type: Optional[str] = None
    description: Optional[str] = None
    weight: Optional[str] = None
    pallets: Optional[str] = None
    delivery_time: Optional[datetime] = None
    comment: Optional[str] = None

    @staticmethod
    async def code_to_text(input_localized_text: List[Dict[str, str]], code: str) -> Union[str, None]:
        for row in input_localized_text:
            for btn_text, callback_data in row.items():
                if callback_data == code:
                    return btn_text

        return ""

    async def form_completion(self, lang: str, db_model: Optional[Order] = None, for_admin: bool = False) -> str:
        model = db_model if db_model else self

        lang_data = localization[lang] if localization.get(lang) else localization[Config.DEFAULT_LANG]
        lang_inline_markups = lang_data["markups"]["inline"]
        lang_misc = lang_data['misc']
        fco = lang_misc["form_completion_order"]

        text = []

        if model.name is not None:
            text.append(f"<b>{hcode(fco['name'])} {model.name}</b>")

        if model.phone_manager is not None:
            text.append(f"<b>{hcode(fco['phone_manager'])} {model.phone_manager}</b>")

        if model.phone_receiver is not None:
            text.append(f"<b>{hcode(fco['phone_receiver'])} {model.phone_receiver}</b>")

        if model.address is not None:
            text.append(f"<b>{hcode(fco['address'])} {model.address}</b>")

        if model.body_type is not None:
            localized_text = await self.code_to_text(
                input_localized_text=lang_inline_markups["body_types"], code=model.body_type)
            text.append(f"<b>{hcode(fco['body_type'])} {localized_text}</b>")

        if model.description is not None:
            text.append(f"<b>{hcode(fco['description'])} {model.description}</b>")

        if model.weight is not None:
            text.append(f"<b>{hcode(fco['weight'])} {model.weight}</b>")

        if model.pallets is not None:
            localized_text = await self.code_to_text(
                input_localized_text=lang_inline_markups["pallets"], code=model.pallets)
            text.append(f"<b>{hcode(fco['pallets'])} {localized_text}</b>")

        if model.delivery_time is not None:
            text.append(f"<b>{hcode(fco['delivery_time'])} {model.delivery_time.strftime('%d.%m.%Y %H:%M')}</b>")

        if model.comment is not None:
            text.append(f"<b>{hcode(fco['comment'])} {model.comment}</b>")

        if for_admin:
            username = (await Config.BOT.get_chat(chat_id=model.tg_user_id)).username
            text.append(f"<b>{hcode(fco['username'])} @{username}</b>")

        return "\n".join(text)
