from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from admin_panel.admin_kb import admin_panel_kb, manage_person_kb, schedule_work_kb

router = Router()

@router.message(Command("start"))
async def admin_panel(message: Message):
    await message.answer("Выберите действие:", reply_markup=admin_panel_kb())


@router.callback_query(F.data == "manage_person")
async def manage_person(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer("Выберите действие по управлению пользователями:", reply_markup=manage_person_kb())

@router.callback_query(F.data == "schedule_work")
async def schedule_work(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer("Выберите действие по управлению расписанием:", reply_markup=schedule_work_kb())

