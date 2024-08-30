from typing import List, TYPE_CHECKING

from sqlalchemy import select, BigInteger, Column, String, Boolean, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.future import select

from src.database.core import Base

class Gets(Base):
    __tablename__ = "Gets"
    __allow_unmapped__ = True

    
    id: int = Column(
        Integer,
        primary_key=True,
        index=True,
        unique=True,
        autoincrement=True
    )
    user_id = Column(BigInteger, index=True)
    post_id = Column(BigInteger)
    text = Column(String)
    media = Column(String)

    @classmethod
    async def get(cls, session: AsyncSession, post_id: int) -> 'Gets':
        user_query = select(cls).filter(cls.post_id == post_id)
        return await session.scalar(user_query)

    @classmethod
    async def addGets(cls, session: AsyncSession, user_id: int, post_id:int, text: str, media: str) -> None:
        new_get = cls(user_id=user_id, post_id=post_id, text=text, media=media)
        session.add(new_get)
        await session.commit()

