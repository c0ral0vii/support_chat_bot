from aiogram.fsm.state import State, StatesGroup


class MessageForm(StatesGroup):
    user_id = State()
    manager_id = State()
