from aiogram.fsm.state import State, StatesGroup


class PageNumberPagination(StatesGroup):
    page = State()
    max_pages = State()
    pages = State()