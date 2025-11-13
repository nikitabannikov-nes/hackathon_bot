from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from admin_panel.admin_kb import get_role_keyboard
from admin_panel.routers.panel import admin_panel

router = Router()

class UserForm(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_full_name = State()
    waiting_for_role = State()

@router.callback_query(F.data == "add_person")
async def add_person(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer(
        "Давайте добавим нового пользователя!\n\n"
        "Введите ID пользователя:",
        reply_markup=None
    )
    await state.set_state(UserForm.waiting_for_user_id)

@router.message(UserForm.waiting_for_user_id, F.text)
async def process_user_id(message: Message, state: FSMContext):
    try:
        user_id = int(message.text)
        await state.update_data(user_id=user_id)
        await message.answer("Отлично! Теперь введите ФИО пользователя:")
        await state.set_state(UserForm.waiting_for_full_name)
    except ValueError:
        await message.answer("Пожалуйста, введите корректный числовой ID:")


@router.message(UserForm.waiting_for_full_name, F.text)
async def process_full_name(message: Message, state: FSMContext):
    full_name = message.text.strip()

    await state.update_data(full_name=full_name)
    await message.answer(
        "Теперь выберите роль пользователя:",
        reply_markup=get_role_keyboard()
    )
    await state.set_state(UserForm.waiting_for_role)


@router.message(UserForm.waiting_for_role, F.text)
async def process_role(message: Message, state: FSMContext):
    role = message.text

    if role not in ["Начальник отдела", "Проверяющий"]:
        await message.answer(
            "Пожалуйста, выберите роль из предложенных вариантов:",
            reply_markup=get_role_keyboard()
        )
        return

    user_data = await state.get_data()

    # РЕГИСТРАЦИЯ ПОЛЬЗОВАТЕЛЯ

    await admin_panel(message)

