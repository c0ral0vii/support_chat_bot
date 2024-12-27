import asyncio

from aiogram import Router, F, types, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from logger.logger import setup_logger
from src.services.bot.handlers.client import _request
from src.services.bot.keyboards.inline.change_category_kb import change_category_kb
from src.services.bot.keyboards.inline.rating_client import create_rating
from src.services.bot.keyboards.inline.subcategory_manager import get_subcategory_markup
from src.services.database.orm.create_request import accept_request, close_request_status, \
    get_request as get_data_request, redirect_request
from src.services.database.models import RequestCategory, UserCategory, RequestSubCategory
from src.services.bot.keyboards.inline.answer_kb import answer_manager_keyboard
from src.services.bot.fsm.client_fsm import RequestSend
from src.services.database.orm.managers import get_manager
from src.services.statistic.services import StatisticService
from src.services.task_control.services import TaskControlService, TASK_CONTROL_SERVICE

clo_manager_router = Router(name='clo_manager')

logger = setup_logger(__name__)


@clo_manager_router.callback_query(lambda query: "start_chat_" in query.data)
async def get_request(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    """Принятие запроса"""

    manager_id = callback.from_user.id
    callback_data = callback.data.split("_")
    logger.info(f"Менеджер {manager_id} - принял запрос - {callback_data[-1]}")

    data = {
        "manager_id": int(manager_id),
        "request_id": int(callback_data[-1]),
        "status": RequestCategory.ORDER,
    }

    request = await accept_request(request_id=data["request_id"], manager_id=data["manager_id"])

    if isinstance(request, dict):
        await callback.message.answer(f"Заказ уже был принят")
        return

    if request is None:
        await callback.message.answer("Ошибка в принятии заказа")
        return

    await state.set_state(RequestSend.request)
    await state.update_data(request=request, manager=True)

    await callback.message.answer(f"Вы приняли запрос под номером - {request.id}.\n\n ИНН: {request.contact_number_or_inn}",
                                  reply_markup=answer_manager_keyboard(request_id=int(request.id), user_id=manager_id))


@clo_manager_router.callback_query(lambda query: "change_category_chat_" in query.data)
async def up_request(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    """Поднять запрос выше"""

    manager_id = callback.from_user.id
    callback_data = callback.data.split("_")
    logger.info(f"Менеджер {manager_id} - меняет категорию у запроса - {callback_data[-1]}")
    request_model = await get_data_request(request_id=int(callback_data[-1]), full_model=True)
    if request_model.close:
        await callback.message.answer("Заявка закрыта.")
        return

    await callback.message.answer("На какую категорию вы хотите поменять запрос:",
                                  reply_markup=change_category_kb(request_id=callback_data[-1]))



@clo_manager_router.callback_query(lambda query: "change_to_" in query.data)
async def change_category(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    callback_data = callback.data.split("_")
    to_category = None
    status = None
    request_model = await get_data_request(request_id=int(callback_data[-1]), full_model=True)

    if request_model.close:
        await callback.message.answer("Заявка закрыта.")
        return

    if callback_data[-2] == "clo":
        to_category = UserCategory.CLO_MANAGER
        status = RequestCategory.ORDER

    if callback_data[-2] == "director":
        to_category = UserCategory.EXECUTIVE_DIRECTOR
        status = RequestCategory.PAYMENT

    if callback_data[-2] == "account":
        to_category = UserCategory.ACCOUNT_MANAGER
        status = RequestCategory.ACCOUNT

    message_text = f"На вас перенаправлен запрос -> {request_model.id} <-> (Номер договора/ИНН: {request_model.contact_number_or_inn}, ID: {request_model.user_id}) отправил запрос по взаиморасчетам."

    if status is None or to_category is None:
        logger.error("Ошибка при перенаправлении")
        await callback.message.answer("Произошла ошибка при перенаправлении")
        return

    data = {
        "message_text": message_text,
        "request_id": int(callback_data[-1]),
        "user_category": to_category,
        "status": status,
    }

    stop_output = await TASK_CONTROL_SERVICE.stop_task(request_id=int(callback_data[-1]))

    if stop_output:
        await callback.message.delete()
        output = await redirect_request(request_id=int(callback_data[-1]), data=data)

        await _request(callback=callback, bot=bot, state=state, data=data, create=False)
        await state.clear()
        await callback.message.answer("Запрос перенаправлен")
    else:
        await callback.message.answer(f"Не удалось перенести на другую категорию так как кто то уже перенёс этот заказ")


@clo_manager_router.callback_query(lambda query: "close_chat_" in query.data)
async def close_request(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    """Закрыть запрос"""

    manager_id = callback.from_user.id
    callback_data = callback.data.split("_")
    logger.info(f"Менеджер {manager_id} - закрыл запрос - {callback_data[-1]}")

    data = {
        "manager_id": int(manager_id),
        "request_id": int(callback_data[-1]),
    }

    close_status = await close_request_status(request_id=data.get("request_id"), only_user=True, user_id=manager_id)



    if close_status["status"] == 200:
        await callback.message.answer(f"Запрос - {data["request_id"]} закрыт выберете, подкатегорию: ", reply_markup=get_subcategory_markup(request_id=data["request_id"]))

        await _close_request(request_id=data["request_id"], bot=bot)
    else:
        await callback.message.answer("Заказ может закрыть только менеджер отвечающий за него")
    await state.clear()


async def _close_request(bot: Bot, request_id: int):
    data = await get_data_request(request_id=request_id)

    await bot.send_message(chat_id=data['request_user_id'], text="Спасибо, что обратились в чат поддержки! Пожалуйста, оцените работу наших менеджеров от 1 до 5 (где 1 – очень плохо, 5 -отлично, вопрос решен).", reply_markup=create_rating(request_id=request_id))