# init_db.py
import asyncio
from app_v1.core import db_helper
from app_v1.models.base import Base

from app_v1.models import base
from app_v1.models import user
from app_v1.models import resume


async def init_models():
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(init_models())
