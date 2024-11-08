from aiogram.fsm.state import State, StatesGroup


class MessageForm(StatesGroup):
    request_id = State()
    user_id = State()
    manager_id = State()
