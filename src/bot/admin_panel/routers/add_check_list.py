from io import BytesIO

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import pandas as pd

from src.bot.admin_panel.admin_kb import admin_panel_kb

router = Router()

class CheckListForm(StatesGroup):
    waiting_for_file = State()


@router.callback_query(F.data == "add_check_list")
async def add_check_list(call: CallbackQuery, state: FSMContext):
    await call.message.delete()

    await call.message.answer(
        "📋 <b>Загрузка чек-листа</b>\n\n"
        "Пожалуйста, отправьте Excel файл (.xlsx, .xls) с чек-листом.\n\n"
        "<i>Файл должен быть в формате Excel</i>",
        parse_mode="HTML"
    )
    await state.set_state(CheckListForm.waiting_for_file)
    await call.answer()


@router.message(CheckListForm.waiting_for_file, F.document)
async def process_excel_file(message: Message, state: FSMContext):
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
        'file_name': document.file_name
    }

    await message.answer(
        f"✅ <b>Excel файл получен!</b>",
        parse_mode="HTML"
    )
    await message.answer("Вы в главном меню", reply_markup=admin_panel_kb())

    print(await process_checklist_file(message.bot, file_info)) # Сделать занос в бд чек-листа

    await state.clear()


@router.message(CheckListForm.waiting_for_file)
async def wrong_file_format(message: Message):
    await message.answer(
        "❌ <b>Это не Excel файл!</b>\n\n"
        "Пожалуйста, отправьте именно <b>документ</b> в формате Excel (.xlsx или .xls)\n\n"
        "Убедитесь, что вы отправляете файл, а не фотографию или текст.",
        parse_mode="HTML"
    )


async def process_checklist_file(bot, file_info: dict):
    try:
        file = await bot.get_file(file_info['file_id'])
        downloaded_file = await bot.download_file(file.file_path)

        df = pd.read_excel(
            BytesIO(downloaded_file.getvalue()),
            engine='openpyxl',
            header=None
        )

        return get_non_empty_values(df)

    except Exception as e:
        print(f"Ошибка: {e}")
        return []


def get_non_empty_values(df: pd.DataFrame) -> list:
    """
    Возвращает все не пустые значения из первого столбца
    """
    result = []

    for i in range(len(df)):
        value = df.iat[i, 0]
        if pd.notna(value) and str(value).strip() != '':
            result.append(str(value).strip())

    return result