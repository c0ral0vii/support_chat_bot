from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def executive_director_keyboards():
    all_requests = KeyboardButton(text="Получить все запросы")
    autoincrement = KeyboardButton(text="Установить автоответ")

    keyboard = ReplyKeyboardMarkup(keyboard=[
        [all_requests, autoincrement],
    ],
    resize_keyboard=True,
    )

    return keyboard