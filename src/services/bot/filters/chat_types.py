from aiogram.filters import Filter
from aiogram import Bot, types
from config import ADMINS_LIST, CLO_MANAGER, SENIOR_CLO_MANAGER, ACCOUNT_MANAGER, EXECUTIVE_DIRECTOR

# admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())

class ChatTypeFilter(Filter):
    def __init__(self, chat_types: list[str]) -> None:
        self.chat_types = chat_types

    async def __call__(self, message: types.Message) -> bool:
        return message.chat.type in self.chat_types

class IsAdmin(Filter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: types.Message, bot: Bot) -> bool:
        return message.from_user.id in ADMINS_LIST

class IsCLOManager(Filter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: types.Message, bot: Bot) -> bool:
        return message.from_user.id in CLO_MANAGER

class IsSeniorCLOManager(Filter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: types.Message, bot: Bot) -> bool:
        return message.from_user.id in SENIOR_CLO_MANAGER

class IsAccountManager(Filter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: types.Message, bot: Bot) -> bool:
        return message.from_user.id in ACCOUNT_MANAGER

class IsExecutiveDirector(Filter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: types.Message, bot: Bot) -> bool:
        return message.from_user.id in EXECUTIVE_DIRECTOR
