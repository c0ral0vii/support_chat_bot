from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def create_rating(request_id):
    rating = []

    for i in range(5):
        rating.append(InlineKeyboardButton(text=f'{i}', callback_data=f"rating_{i}_{request_id}"))

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        rating
    ])
    return keyboard