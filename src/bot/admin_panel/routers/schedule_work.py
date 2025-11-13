from datetime import datetime
from typing import List, Dict, Any

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import pandas as pd
from io import BytesIO

from src.bot.admin_panel.admin_kb import admin_panel_kb

router = Router()

class ScheduleForm(StatesGroup):
    waiting_for_schedule_file = State()


@router.callback_query(F.data == "add_schedule")
async def add_schedule(call: CallbackQuery, state: FSMContext):
    await call.message.delete()

    await call.message.answer(
        "📅 <b>Загрузка расписания</b>\n\n"
        "Пожалуйста, отправьте Excel файл (.xlsx, .xls) с расписанием.\n\n"
        "<i>Файл должен быть в формате Excel</i>",
        parse_mode="HTML"
    )
    await state.set_state(ScheduleForm.waiting_for_schedule_file)
    await call.answer()


@router.message(ScheduleForm.waiting_for_schedule_file, F.document)
async def process_schedule_file(message: Message, state: FSMContext):
    document = message.document

    file_name = document.file_name.lower()

    if not (file_name.endswith('.xlsx') or file_name.endswith('.xls')):
        await message.answer(
            "❌ <b>Неверный формат файла!</b>\n\n"
            "Пожалуйста, отправьте файл в формате Excel (.xlsx или .xls)",
            parse_mode="HTML"
        )
        return

    file_info = {
        'file_id': document.file_id,
        'file_name': document.file_name,
        'file_size': document.file_size
    }

    await state.update_data(file_info=file_info)

    await message.answer(
        f"✅ Excel файл с расписанием получен!"
    )
    await message.answer("Вы в главном меню", reply_markup=admin_panel_kb())

    await process_schedule_excel(message.bot, file_info)

    await state.clear()


@router.message(ScheduleForm.waiting_for_schedule_file)
async def wrong_schedule_file_format(message: Message):
    await message.answer(
        "❌ <b>Это не Excel файл!</b>\n\n"
        "Пожалуйста, отправьте именно <b>документ</b> в формате Excel (.xlsx или .xls)\n\n"
        "Убедитесь, что вы отправляете файл, а не фотографию или текст.",
        parse_mode="HTML"
    )

async def process_schedule_excel(bot, file_info: dict):
    try:
        file = await bot.get_file(file_info['file_id'])
        downloaded_file = await bot.download_file(file.file_path)


        df = pd.read_excel(
            BytesIO(downloaded_file.getvalue()),
            engine='openpyxl',
            header=None
        )

        print(parse_schedule_excel(df))

        result = parse_schedule_excel(df)
        #вернет массив словарей {'cleaner_id': 'cleaner_id', 'inspector_id': 'inspectior_id', 'cheklist_id': 'cheklist_id', 'area': 'area', 'date': 'date', 'created_at': datetime.date(2025, 11, 13), 'status': 'planned', 'updated_at': None}

    except Exception as e:
        print(f"Ошибка при обработке файла расписания: {e}")


def parse_schedule_excel(df: pd.DataFrame) -> List[Dict[str, Any]]:

    if df.empty:
        return []

    df.columns = ['cleaner_id', 'inspector_id', 'cheklist_id', 'area', 'date']


    today_date = datetime.now().date()


    result = []
    for _, row in df.iterrows():
        record = {
            'cleaner_id': row['cleaner_id'],
            'inspector_id': row['inspector_id'],
            'cheklist_id': row['cheklist_id'],
            'area': row['area'],
            'date': row['date'],
            'created_at': today_date,
            'status': 'planned',
            'updated_at': None
        }
        result.append(record)

    return result
