from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def answer_keyboard(user_id: int):
    '''
    Ответ пользователю
    '''

    answer = InlineKeyboardButton(text='Принять заявку', callback_data=f'start_chat_{user_id}')
    up = InlineKeyboardButton(text='Поднять заявку', callback_data=f'up_chat_{user_id}')
    cancel = InlineKeyboardButton(text='Отменить заявку', callback_data=f'cancel_chat_{user_id}')
    close = InlineKeyboardButton(text='Закрыть заявку', callback_data=f'close_chat_{user_id}')

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [answer],
        [up, cancel],
        [close]
    ])

    return keyboard


def answer_client_keyboard(manager_id: int):
    '''
    Ответ менеджеру
    '''

    send_message = InlineKeyboardButton(text='Отправить сообщение', callback_data=f'send_message_{manager_id}')

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [send_message]
    ])

    return keyboard


def answer_manager_keyboard(user_id: int):
    '''
    Ответ менеджера либо закрытие
    '''

    send_message = InlineKeyboardButton(text='Отправить сообщение', callback_data=f'send_message_{user_id}')
    up = InlineKeyboardButton(text='Поднять заявку', callback_data=f'up_chat_{user_id}')
    close = InlineKeyboardButton(text='Закрыть обращение', callback_data=f'close_chat_{user_id}')

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [send_message],
        [up, close]
    ])

    return keyboard