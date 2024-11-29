from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def change_category_kb(request_id):
    order = InlineKeyboardButton(text="Менеджеры КЛО", callback_data=f"change_to_clo_{request_id}")
    payment = InlineKeyboardButton(text="Исполнительный директор", callback_data=f"change_to_director_{request_id}")
    account = InlineKeyboardButton(text="Менеджеры по сопровождению", callback_data=f"change_to_account_{request_id}")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [order],
        [payment],
        [account],
    ])

    return keyboard