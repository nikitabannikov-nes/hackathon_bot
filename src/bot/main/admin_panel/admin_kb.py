from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton



def schedule_work_kb():
    buttons = [
        [InlineKeyboardButton(text="Изменить расписание", callback_data="add_schedule")],
        [InlineKeyboardButton(text="Добавить расписание", callback_data="add_schedule")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def manage_person_kb():
    buttons = [
        [InlineKeyboardButton(text="Добавить сотрудника", callback_data="add_person")],
        [InlineKeyboardButton(text="Удаление сотрудника", callback_data="del_person")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def admin_panel_kb():
    buttons = [
        [InlineKeyboardButton(text="Управление пользователями", callback_data="manage_person")],
        [InlineKeyboardButton(text="Добавить чек-лист", callback_data="add_check_list")],
        [InlineKeyboardButton(text="Работа с графиками", callback_data="schedule_work")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_role_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Начальник отдела")],
            [KeyboardButton(text="Проверяющий")]
        ],
        resize_keyboard=True
    )

def get_confirmation_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да", callback_data="confirm_yes"),
                InlineKeyboardButton(text="❌ Нет", callback_data="confirm_no")
            ]
        ]
    )


def get_cancel_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel")]
        ]
    )
