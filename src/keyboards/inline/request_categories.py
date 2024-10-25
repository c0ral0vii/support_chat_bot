from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def request_categories_keyboard():
    order = InlineKeyboardButton(text="Вопрос по заявке/заказу", callback_data="order_request")
    payment = InlineKeyboardButton(text="Вопрос по взаиморасчётам", callback_data="payment_request")
    account = InlineKeyboardButton(text="Вопрос по личному кабинету", callback_data="account_request")
    other = InlineKeyboardButton(text="Другое", callback_data="other_request")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [order],
        [payment],
        [account],
        [other]
    ])

    return keyboard