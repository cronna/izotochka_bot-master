from os import getenv
from dotenv import load_dotenv
from aiogram import Bot

load_dotenv()
bot = Bot(token=getenv('BOT_TOKEN'))