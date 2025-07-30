from datetime import datetime
from typing import Optional

from aiogram.utils.markdown import hcode
from pydantic import BaseModel

from config import Config
from tg_bot.db_models.schemas import Order
from tg_bot.misc.utils import localization


class OrderForm(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    weight: Optional[str] = None
    pallets: Optional[str] = None
    delivery_time: Optional[datetime] = None
    comment: Optional[str] = None

    async def form_completion(self, lang: str, db_model: Optional[Order] = None, for_admin: bool = False) -> str:
        model = db_model if db_model else self

        lang_data = localization[lang] if localization.get(lang) else localization[Config.DEFAULT_LANG]
        lang_misc = lang_data['misc']
        fco = lang_misc["form_completion_order"]

        text = []

        if model.name is not None:
            text.append(f"<b>{hcode(fco['name'])} {model.name}</b>")

        if model.phone is not None:
            text.append(f"<b>{hcode(fco['phone'])} {model.phone}</b>")

        if model.address is not None:
            text.append(f"<b>{hcode(fco['address'])} {model.address}</b>")

        if model.description is not None:
            text.append(f"<b>{hcode(fco['description'])} {model.description}</b>")

        if model.weight is not None:
            text.append(f"<b>{hcode(fco['weight'])} {model.weight}</b>")

        if model.pallets is not None:
            text.append(f"<b>{hcode(fco['pallets'])} {model.pallets}</b>")

        if model.delivery_time is not None:
            text.append(f"<b>{hcode(fco['delivery_time'])} {model.delivery_time.strftime('%d.%m.%Y %H:%M')}</b>")

        if model.comment is not None:
            text.append(f"<b>{hcode(fco['comment'])} {model.comment}</b>")

        if for_admin:
            username = (await Config.BOT.get_chat(chat_id=model.tg_user_id)).username
            text.append(f"<b>{hcode(fco['username'])} @{username}</b>")

        return "\n".join(text)
