import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from src.bot.application.repositories.user_repository import UserRepository
from src.bot.application.use_cases.user import UserUseCases

load_dotenv()

bot = Bot(token=os.getenv('BOT_TOKEN'))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
user_repository = UserRepository()
user_use_cases = UserUseCases(user_repository)



@dp.message(Command("start"))
async def start_comand(message: types.Message):
    await user_use_cases.start_comand(message)




@dp.message(lambda message: message.text in ["Управление сотрудниками", "Выложить график", "Добавить чеклист"])
async def handle_admin_buttons(message: types.Message):
    user_id = message.from_user.id
    role = get_user_role(user_id)
    
    if role == 'admin':
        if message.text == "Управление сотрудниками":
            await message.answer("Раздел управления сотрудниками...")
        elif message.text == "Выложить график":
            await message.answer("Раздел выкладки графика...")
        elif message.text == "Добавить чеклист":
            await message.answer("Раздел добавления чеклиста...")



            
@dp.message(lambda message: message.text == "Просмотреть статистику")
async def handle_stats(message: types.Message):
    user_id = message.from_user.id
    role = get_user_role(user_id)
    
    if role == 'user':
        # Логика для пользователя
        await message.answer("Ваша статистика...")

@dp.message(lambda message: message.text == "Просмотреть график проверок")
async def handle_schedule(message: types.Message):
    user_id = message.from_user.id
    role = get_user_role(user_id)
    
    if role == 'inspector':
        # Логика для проверяющего
        await message.answer("График проверок...")