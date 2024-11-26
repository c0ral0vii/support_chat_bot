from aiogram.fsm.state import State, StatesGroup


class MessageForm(StatesGroup):
    text = State()
