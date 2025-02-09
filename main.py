import asyncio

from aiogram import Bot, Dispatcher

from aiogram.fsm.storage.memory import MemoryStorage
from commands import user_router


async def main():
    bot = Bot(token="You bot token")

    storage = MemoryStorage()

    dp = Dispatcher(storage=storage)

    dp.include_router(user_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
