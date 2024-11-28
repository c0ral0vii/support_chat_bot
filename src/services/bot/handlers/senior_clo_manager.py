from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext

from logger.logger import setup_logger


senior_clo_router = Router(name='Senior CLO')
logger = setup_logger(__name__)


