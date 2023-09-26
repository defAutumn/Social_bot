"""
    Точка входа, код запуска бота и инициализации всех остальных модулей
"""


import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from sqlalchemy import URL

import config
from Bot.db import models
from Bot.handlers.handlers import form_router
from Bot.db.models import PostTransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from Bot.middlewares.db import DbSessionMiddleware


async def main():

    bot = Bot(token=config.TOKEN, parse_mode=ParseMode.MARKDOWN)

    async_engine = create_async_engine(url=config.postgres_url)

    session_maker = async_sessionmaker(async_engine, expire_on_commit=False)

    dp = Dispatcher()
    dp.update.middleware(DbSessionMiddleware(session_pool=session_maker))

    # Register handlers
    dp.include_router(form_router)

    # await proceed_schemas(async_engine, BaseModel.metadata)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
