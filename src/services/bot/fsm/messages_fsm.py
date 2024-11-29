from aiogram.fsm.state import State, StatesGroup


class MessageForm(StatesGroup):
    to = State()
    text = State()
