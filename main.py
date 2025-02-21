import locale
from sys import stdout
from asyncio import run
import asyncio
from os import getenv
from logging import basicConfig, INFO
from dotenv import load_dotenv
from handlers.user.check_pay import check_payment

from aiogram import Dispatcher, Bot
from aiogram.types import BotCommand

from handlers import *
from handlers.user.history import history_router
from handlers.user.profile import profile_router
from handlers.user.admin import admin_router

from utils.models import Users, Services, Category, PaymentsT, Stud,St_per,inv,invd, AdminUsers, StudentCourses

load_dotenv()
bot = Bot(token=getenv('BOT_TOKEN'))
dp = Dispatcher()

dp.include_routers(
    start_router, 
    user_services_router, 
    registration_router, 
    buy_router,
    history_router,
    profile_router,
    admin_router
)

async def main():
    tables = [Users, Services, Category, PaymentsT, Stud, St_per, inv, invd, AdminUsers, StudentCourses]
    for table in tables:
        if not table.table_exists():
            table.create_table()

    print('started')
    basicConfig(level=INFO, stream=stdout)
    # basicConfig(filename='logs.log', level=INFO)
    await bot.set_my_commands([BotCommand(command='start', description='Главное меню')])
    task_chkPay=asyncio.create_task(check_payment(bot))
    task_bot=asyncio.create_task(dp.start_polling(bot))
    #await dp.start_polling(bot)
    await task_chkPay
    await task_bot


    
if __name__ == "__main__":
        run(main())
    
