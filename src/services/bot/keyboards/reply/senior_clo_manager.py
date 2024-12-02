from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def senior_clo_manager():
    all_requests = KeyboardButton(text="Получить все запросы")

    keyboard = ReplyKeyboardMarkup(keyboard=[
        [all_requests]
    ],
    resize_keyboard=True)

    return keyboard