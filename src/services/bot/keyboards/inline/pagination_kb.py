from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.services.database.models import Request


async def pagination_kb(list_requests: List[Request], page: int = 1, max_page = ".."):
    requests = []

    for request in list_requests:
        requests.append([InlineKeyboardButton(text=f"ID:{request.id}-{"✅" if request.close else '❌'}-{request.contact_number_or_inn[:5]}-{request.request_category.value}", callback_data=f"detail_{request.id}")])

    refresh = InlineKeyboardButton(text='Перезагрузить', callback_data='refresh')
    left_button = InlineKeyboardButton(text='<', callback_data='left_pagination')
    page_button = InlineKeyboardButton(text=f'{page}/{max_page}', callback_data='page_pagination')
    right_button = InlineKeyboardButton(text='>', callback_data='right_pagination')

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        *requests,
        [left_button, page_button, right_button],
        [refresh],
    ])

    return keyboard
