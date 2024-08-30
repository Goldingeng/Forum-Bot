import time
from typing import List, TYPE_CHECKING

from sqlalchemy import select, BigInteger, Column, String, Boolean
from sqlalchemy.ext.asyncio import AsyncSession


from src.database.core import Base

from sqlalchemy import update

class User(Base):
    __tablename__ = "Users"
    __allow_unmapped__ = True

    id: int = Column(
        BigInteger,
        primary_key=True,
        index=True,
        unique=True
    )

    nickname: str = Column(String)

    ban_status: bool = Column(Boolean, default=False)

    admin_ban: int = Column(BigInteger, default=0)

    @classmethod
    async def get(cls, session: AsyncSession, user_id: int) -> 'User':
        user_query = select(cls).filter(cls.id == user_id)
        return await session.scalar(user_query)
    
    @classmethod
    async def add(cls, session: AsyncSession, user_id: int, nickname: str) -> 'User':
        user = await cls.get(session, user_id)

        if user is None:
            user = cls(id=user_id, nickname=nickname)
            session.add(user)
            await session.commit()

        return user

    @classmethod
    async def ban(cls, session: AsyncSession, user_id: int, admin_id: int) -> None:
        user = await cls.get(session, user_id)
        if user is None:
            return False
        
        update_query = update(cls).where(cls.id == user_id).values(ban_status=True, admin_ban=admin_id)
        await session.execute(update_query)
        await session.commit()
        
    @classmethod
    async def unban(cls, session: AsyncSession, user_id: int, admin_id: int) -> None:
        user = await cls.get(session, user_id)
        if user is None:
            return False
        
        update_query = update(cls).where(cls.id == user_id).values(ban_status=False, admin_ban=admin_id)
        await session.execute(update_query)
        await session.commit()
    
    @classmethod
    async def is_banned(cls, session: AsyncSession, user_id: int) -> bool:
        user = await cls.get(session, user_id)
        if user is None:
            return False
        return user.ban_status