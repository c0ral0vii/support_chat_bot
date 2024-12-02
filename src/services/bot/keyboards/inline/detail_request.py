from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def detail_request(request_id: int):
    get_messages = InlineKeyboardButton(text='Выгрузить переписку', callback_data=f"export_messages_{request_id}")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [get_messages],
    ])

    return kb