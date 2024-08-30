import time
from typing import List, TYPE_CHECKING

from sqlalchemy import select, BigInteger, Column, String, Boolean
from sqlalchemy.ext.asyncio import AsyncSession


from src.database.core import Base

from sqlalchemy import update

class Admin(Base):
    __tablename__ = "Admin"
    __allow_unmapped__ = True

    id: int = Column(
        BigInteger,
        primary_key=True,
        index=True,
        unique=True
    )
    admin_status: int = Column(BigInteger, default=5)

    @classmethod
    async def get(cls, session: AsyncSession, user_id: int) -> 'Admin':
        user_query = select(cls).filter(cls.id == user_id)
        return await session.scalar(user_query)


    @classmethod
    async def revoke_admin_status(cls, session: AsyncSession, user_id: int) -> None:
        await cls.add_admin(session, user_id, admin_status=0)

    @classmethod
    async def add_admin(cls, session: AsyncSession, user_id: int, admin_status: int) -> 'bool':
        admin = await cls.get(session, user_id)

        if admin is None:
            admin = cls(id=user_id, admin_status=5)
            session.add(admin)
            await session.commit()

        return True