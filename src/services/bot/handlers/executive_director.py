from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext

from logger.logger import setup_logger


executive_director_router = Router(name='Executive director')
logger = setup_logger(__name__)


# TODO подстроить под его клавиатуру