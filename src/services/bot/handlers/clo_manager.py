from aiogram import Router, F, types, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from logger.logger import setup_logger
from src.services.bot.keyboards.inline.rating_client import create_rating
from src.services.bot.keyboards.inline.subcategory_manager import get_subcategory_markup
from src.services.database.orm.create_request import accept_request, close_request_status, get_request as get_data_request
from src.services.database.models import RequestCategory
from src.services.bot.keyboards.inline.answer_kb import answer_manager_keyboard
from src.services.bot.fsm.client_fsm import RequestSend

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

    if type(request) == dict:
        await callback.message.answer(f"Заказ уже был принят")
        return

    if request is None:
        await callback.message.answer("Ошибка в принятии заказа")
        return

    await state.set_state(RequestSend.request)
    await state.update_data(request=request, manager=True)

    await callback.message.answer(f"Вы приняли запрос под номером - {request.id}.", reply_markup=answer_manager_keyboard(request_id=request.id, user_id=manager_id))


@clo_manager_router.callback_query(lambda query: "change_category_chat_" in query.data)
async def up_request(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    """Поднять запрос выше"""

    manager_id = callback.from_user.id
    callback_data = callback.data.split("_")
    logger.info(f"Менеджер {manager_id} - поменял категорию запроса - {callback_data[-1]}")

    # data = {
    #     "request_id": int(callback_data[-1]),
    #     "user_category": ,
    #     "status": ,
    # }


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

    close_status = await close_request_status(request_id=data.get("request_id"))

    if close_status["status"] == 200:
        await callback.message.answer(f"Запрос - {data["request_id"]} закрыт выберете, подкатегорию: ", reply_markup=get_subcategory_markup(request_id=data["request_id"]))

        await _close_request(request_id=data["request_id"], bot=bot)

    await state.clear()


async def _close_request(bot: Bot, request_id: int):
    data = await get_data_request(request_id=request_id)

    await bot.send_message(chat_id=data['request_user_id'], text="Спасибо, что обратились в чат поддержки! Пожалуйста, оцените работу наших менеджеров от 1 до 5 (где 1 – очень плохо, 5 -отлично, вопрос решен).", reply_markup=create_rating(request_id=request_id))