from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def detail_request(request_id: int):
    close = InlineKeyboardButton(text='Закрыть обращение', callback_data=f'close_chat_{request_id}')
    get_messages = InlineKeyboardButton(text='Выгрузить переписку', callback_data=f"export_messages_{request_id}")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [close],
        [get_messages],
    ])

    return kb