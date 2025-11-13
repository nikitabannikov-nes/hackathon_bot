from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_admin_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Управление сотрудниками"), KeyboardButton(text="Выложить график")],
            [KeyboardButton(text="Добавить чеклист")]
        ],
        resize_keyboard=True
    )

def get_inspector_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Просмотреть график проверок")]],
        resize_keyboard=True
    )

def get_user_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Просмотреть статистику")]],
        resize_keyboard=True
    )