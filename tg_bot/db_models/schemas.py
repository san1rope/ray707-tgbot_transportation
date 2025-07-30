from sqlalchemy import Column, BigInteger, String, Integer, sql, DateTime

from tg_bot.db_models.db_gino import TimedBaseModel

prefix = "tg-bot_transportation_"


class User(TimedBaseModel):
    __tablename__ = prefix + "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_user_id = Column(BigInteger, primary_key=True, nullable=False)
    language = Column(String)

    query: sql.Select


class Order(TimedBaseModel):
    __tablename__ = prefix + "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_user_id = Column(BigInteger, primary_key=True, nullable=False)
    status = Column(Integer, nullable=False)

    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    address = Column(String, nullable=False)
    description = Column(String)
    weight = Column(String, nullable=False)
    pallets = Column(String)
    delivery_time = Column(DateTime, nullable=False)
    comment = Column(String)

    query: sql.Select
