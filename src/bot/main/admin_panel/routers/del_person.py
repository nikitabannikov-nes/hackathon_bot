from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from admin_panel.admin_kb import get_cancel_keyboard, get_confirmation_keyboard, admin_panel_kb

router = Router()

class UserIDForm(StatesGroup):
    waiting_for_id = State()
    waiting_for_confirmation = State()

@router.callback_query(F.data == "del_person")
async def start_get_id(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer(
        "🔢 Введите ID пользователя:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(UserIDForm.waiting_for_id)


@router.message(UserIDForm.waiting_for_id, F.text)
async def process_user_id(message: Message, state: FSMContext):
    try:
        user_id = int(message.text)

        # Сохраняем ID в состоянии
        await state.update_data(user_id=user_id)

        # Запрашиваем подтверждение
        await message.answer("Вы уверены, что хотите удалить пользователя?",
            reply_markup=get_confirmation_keyboard()
        )
        await state.set_state(UserIDForm.waiting_for_confirmation)

    except ValueError:
        await message.answer(
            "❌ Пожалуйста, введите корректный числовой ID:",
            reply_markup=get_cancel_keyboard()
        )


@router.callback_query(UserIDForm.waiting_for_confirmation, F.data == "confirm_yes")
async def confirm_id(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    user_id = user_data['user_id']

    await callback.message.edit_text(
        f"✅ Пользователь с ID <b>{user_id}</b> успешно удален!",
        parse_mode="HTML"
    )

    # Удаление пользователя

    await state.clear()
    await callback.answer("✅ Пользователь удален!")
    await callback.message.answer("Панель управления:", reply_markup=admin_panel_kb())



# Отказ от подтверждения
@router.callback_query(UserIDForm.waiting_for_confirmation, F.data == "confirm_no")
async def reject_id(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🔄 Введите ID пользователя заново:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(UserIDForm.waiting_for_id)
    await callback.answer("🔄 Введите ID заново")


@router.callback_query(F.data == "cancel")
async def cancel_operation(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Операция отменена.")
    await callback.message.answer("Панель управления:", reply_markup=admin_panel_kb())

