import logging
import traceback
from datetime import datetime
from typing import Optional, Union, List

from asyncpg import UniqueViolationError
from sqlalchemy import and_

from .schemas import *

logger = logging.getLogger(__name__)


class DbUser:
    def __init__(self, db_id: Optional[int] = None, tg_user_id: Optional[int] = None):
        self.db_id = db_id
        self.tg_user_id = tg_user_id

    async def add(self) -> Union[User, bool]:
        try:
            target = User(tg_user_id=self.tg_user_id)
            return await target.create()

        except UniqueViolationError:
            logger.error(traceback.format_exc())
            return False

    async def select(self) -> Union[User, List[User], bool, None]:
        try:
            q = User.query

            if self.db_id:
                return await q.where(User.id == self.db_id).gino.first()

            elif self.tg_user_id:
                return await q.where(User.tg_user_id == self.tg_user_id).gino.first()

            else:
                return await q.gino.all()

        except Exception:
            logger.error(traceback.format_exc())
            return False

    async def update(self, **kwargs) -> bool:
        try:
            if not kwargs:
                return False

            target = await self.select()
            return await target.update(**kwargs).apply()

        except Exception:
            logger.error(traceback.format_exc())
            return False

    async def remove(self) -> Union[bool, List[bool]]:
        try:
            target = await self.select()
            if isinstance(target, list):
                results = []
                for i in target:
                    results.append(await i.delete())

                return results

            elif isinstance(target, User):
                return await target.delete()

        except Exception:
            logger.error(traceback.format_exc())
            return False


class DbOrder:
    def __init__(self, db_id: Optional[int] = None, tg_user_id: Optional[int] = None, status: Optional[int] = None,
                 name: Optional[str] = None, phone_manager: Optional[str] = None, phone_receiver: Optional[str] = None,
                 address: Optional[str] = None, description: Optional[str] = None, weight: Optional[str] = None,
                 pallets: Optional[str] = None, delivery_time: Optional[datetime] = None,
                 comment: Optional[str] = None, body_type: Optional[str] = None):
        self.db_id = db_id
        self.tg_user_id = tg_user_id
        self.status = status
        self.name = name
        self.phone_manager = phone_manager
        self.phone_receiver = phone_receiver
        self.address = address
        self.body_type = body_type
        self.description = description
        self.weight = weight
        self.pallets = pallets
        self.delivery_time = delivery_time
        self.comment = comment

    async def add(self) -> Union[Order, bool]:
        try:
            target = Order(tg_user_id=self.tg_user_id, status=self.status, name=self.name, body_type=self.body_type,
                           phone_manager=self.phone_manager, phone_receiver=self.phone_receiver, address=self.address,
                           description=self.description, weight=self.weight, pallets=self.pallets,
                           delivery_time=self.delivery_time, comment=self.comment)
            return await target.create()

        except UniqueViolationError:
            logger.error(traceback.format_exc())
            return False

    async def select(self) -> Union[Order, List[Order], bool, None]:
        try:
            q = Order.query

            if self.db_id is not None:
                return await q.where(Order.id == self.db_id).gino.first()

            elif (self.tg_user_id is not None) and (self.status is not None):
                return await q.where(and_(Order.tg_user_id == self.tg_user_id, Order.status == self.status)).gino.all()

            elif self.tg_user_id is not None:
                return await q.where(Order.tg_user_id == self.tg_user_id).gino.all()

            elif self.status is not None:
                return await q.where(Order.status == self.status).gino.all()

            elif self.status is not None:
                return await q.where(Order.status == self.status).gino.all()

            else:
                return q.gino.all()

        except Exception:
            logger.error(traceback.format_exc())
            return False

    async def update(self, **kwargs) -> bool:
        try:
            if not kwargs:
                return False

            target = await self.select()
            return await target.update(**kwargs).apply()

        except Exception:
            logger.error(traceback.format_exc())
            return False
