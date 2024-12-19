import asyncio

from aiogram import Bot, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, StateFilter
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from logger.logger import setup_logger
from src.services.database.models import UserCategory, RequestCategory, Request, Manager
from src.services.bot.fsm.client_fsm import ClientForm
from src.services.database.orm.create_request import create_request, get_request
from src.services.database.orm.managers import get_managers, get_manager
from src.services.bot.keyboards.inline.client_kb import request_categories_keyboard
from src.services.bot.keyboards.inline.answer_kb import answer_keyboard, answer_client_keyboard
from src.services.bot.keyboards.reply import (
    senior_clo_manager,
    executive_director_kb
)
from src.services.database.orm.users import create_user
from src.services.task_control.services import TASK_CONTROL_SERVICE
import pytz
import datetime

client_router = Router(name="client")

logger = setup_logger(__name__)


async def get_time():
    moscow_tz = pytz.timezone('Europe/Moscow')
    moscow_time = datetime.datetime.now(moscow_tz)
    return moscow_time


@client_router.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    manager = await get_manager(user_id=user_id)

    if isinstance(manager, Manager):
        if manager.category == UserCategory.EXECUTIVE_DIRECTOR:
            await message.answer("Вы вступили в пост 'Исполнительный директор'.", reply_markup=executive_director_kb.executive_director_keyboards())
            return
        if manager.category == UserCategory.SENIOR_CLO_MANAGER:
            await message.answer("Вы вступили в пост 'Старший менеджер КЛО'.", reply_markup=senior_clo_manager.senior_clo_manager())
            return
        if manager.category == UserCategory.CLO_MANAGER:
            await message.answer("Вы вступили на пост 'Менеджеры КЛО'.")
            return
        if manager.category == UserCategory.ACCOUNT_MANAGER:
            await message.answer("Вы вступили на пост 'Менеджеры по сопровождению'.", reply_markup=senior_clo_manager.senior_clo_manager())
            return

    moscow_time = await get_time()
    if 9 < moscow_time.hour < 19:
        await message.answer(
            "Добрый день, режим работы с 9:00 до 19:00 МСК!\nДля обработки запроса укажите номер договора или ИНН")
        await state.clear()
        await state.set_state(ClientForm.contract_number_or_inn)
    else:
        await message.answer("Ой, все уже ушли домой, как только вернемся на работу, обязательно вам ответим")



@client_router.message(ClientForm.contract_number_or_inn)
async def proccess_contract_number_or_inn(message: types.Message, state: FSMContext) -> None:
    await state.update_data(contract_number_or_inn=message.text)
    await create_user({
        "user_id": int(message.from_user.id),
        "username": message.from_user.username,
    })
    await message.answer("Выберите, пожалуйста, категорию вашего запроса:", reply_markup=request_categories_keyboard())


async def _request(callback: types.CallbackQuery, bot: Bot, state: FSMContext, data: dict, create: bool = True):
    managers = await get_managers()


    messages = []
    logger.debug(data)
    if create:
        request = await create_request(data=data)
    else:
        request = await get_request(request_id=int(data["request_id"]), full_model=True)

    await callback.message.answer("В течение 5 минут с вами свяжется первый освободившийся менеджер.\n\n⚠️ Вы можете описать вашу проблему в одном сообщении снизу.",
                            reply_markup=await answer_client_keyboard(request_id=int(request.id), user_id="no"))

    for i in managers:
        try:
            if isinstance(data["user_category"], list):
                for user_category in data["user_category"]:
                    if i.category == user_category:
                        message = await bot.send_message(chat_id=i.user_id, text=data["message_text"],
                                                         reply_markup=answer_keyboard(request_id=request.id))
                        messages.append(message)
            else:
                if i.category == data['user_category'] and i.free:
                    message = await bot.send_message(chat_id=i.user_id, text=data["message_text"],
                                                     reply_markup=answer_keyboard(request_id=request.id))
                    messages.append(message)

        except TelegramBadRequest as e:
            logger.warning(e)
            continue
        except TelegramForbiddenError as te:
            logger.warning(te)
            continue
        except Exception as e:
            logger.warning(e)
            continue

    logger.debug("разослали все сообщения")


    task = asyncio.create_task(_create_notification(messages=messages, bot=bot, data=data, managers=managers, request=request, max_interval=data.get("max_interval", 999)))
    data_task = {request.id: task}
    await TASK_CONTROL_SERVICE.add_task(task=data_task)
    logger.debug(data_task)


async def _create_notification(messages: list[types.Message], bot: Bot, data: dict, managers: list, request: Request, max_interval: int = 999) -> None:
    interval = 0
    while True:
        await asyncio.sleep(60)
        interval += 1

        check_request = await get_request(request_id=request.id)
        time = await get_time()

        if 9 < time.hour < 19:
            await asyncio.sleep(3600)
            continue

        if check_request["request_manager"] or check_request["request_status"] is True:
            await delete_message(messages)
            return

        if interval == max_interval and max_interval != 30:
            data["max_interval"] = 30
            data["message_text"] = f"!!->Просрочен---{data['message_text']}---Просрочен<-!!"
            data["user_category"] = [UserCategory.SENIOR_CLO_MANAGER, UserCategory.CLO_MANAGER, UserCategory.ACCOUNT_MANAGER]

        if max_interval == 30 and interval == 30:
            await bot.send_message(chat_id=data["user_id"], text="Вы можете связаться со своим закрепленным менеджером.")
            return
            

        skip_user_id = {}
        for i in managers:
            try:
                logger.debug(interval)
                if not data["user_category"] is None:
                    try:
                        if i.category == data['user_category'] and i.free:
                            message = await bot.send_message(chat_id=i.user_id, text=data["message_text"],
                                                             reply_markup=answer_keyboard(request_id=request.id))
                            messages.append(message)

                    except TelegramBadRequest as e:
                        logger.warning(e)
                        continue
                    except TelegramForbiddenError as te:
                        logger.warning(te)
                        continue
                    except Exception as e:
                        logger.warning(e)
                        continue

                if isinstance(data["user_category"], list):
                    for user_category in data["user_category"]:
                        try:
                            if i.category == user_category and i.user_id not in skip_user_id:
                                message = await bot.send_message(chat_id=i.user_id, text=data["message_text"],
                                                                 reply_markup=answer_keyboard(request_id=request.id))
                                messages.append(message)

                        except TelegramBadRequest as e:
                            logger.warning(e)
                            continue
                        except TelegramForbiddenError as te:
                            logger.warning(te)
                            continue
                        except Exception as e:
                            logger.warning(e)
                            continue

            except Exception as e:
                logger.warning(e)
                continue


async def delete_message(messages):
    for message in messages:
        await message.delete()


@client_router.callback_query(lambda c: c.data == "order_request", StateFilter(ClientForm))
async def handle_order_request(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    await callback.message.delete()

    user_id = callback.from_user.id
    username = callback.from_user.username or "Неизвестный пользователь"

    user_data = await state.get_data()
    contract_number_or_inn = user_data.get("contract_number_or_inn", "Не указано")

    message_text = f"Пользователь {username} (Номер договора/ИНН: {contract_number_or_inn}, ID: {user_id}) отправил запрос по теме 'Вопрос по заявке/заказу'."

    data = {
        "message_text": message_text,
        "contact_number_or_inn": contract_number_or_inn,
        "user_id": user_id,
        "status": RequestCategory.ORDER,
        "user_category": [UserCategory.CLO_MANAGER, UserCategory.SENIOR_CLO_MANAGER],
        "max_interval": 5,
    }

    await _request(callback=callback, bot=bot, state=state, data=data)


@client_router.callback_query(lambda c: c.data == "account_request", StateFilter(ClientForm))
async def handle_account_request(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    await callback.message.delete()

    user_id = callback.from_user.id
    username = callback.from_user.username or "Неизвестный пользователь"

    user_data = await state.get_data()
    contract_number_or_inn = user_data.get("contract_number_or_inn", "Не указано")

    message_text = f"Пользователь {username} (Номер договора/ИНН: {contract_number_or_inn}, ID: {user_id}) отправил запрос по теме 'Вопрос по личному кабинету'."

    data = {
        "message_text": message_text,
        "contact_number_or_inn": contract_number_or_inn,
        "user_id": user_id,
        "status": RequestCategory.ACCOUNT,
        "user_category": UserCategory.ACCOUNT_MANAGER,
    }

    await _request(callback=callback, bot=bot, state=state, data=data)


@client_router.callback_query(lambda c: c.data == "other_request", StateFilter(ClientForm))
async def handle_other_request(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    await callback.message.delete()

    user_id = callback.from_user.id
    username = callback.from_user.username or "Неизвестный пользователь"

    user_data = await state.get_data()
    contract_number_or_inn = user_data.get("contract_number_or_inn", "Не указано")

    message_text = f"Пользователь {username} (Номер договора/ИНН: {contract_number_or_inn}, ID: {user_id}) отправил запрос по теме 'Другое'."

    data = {
        "message_text": message_text,
        "contact_number_or_inn": contract_number_or_inn,
        "user_id": user_id,
        "status": RequestCategory.OTHER,
        "user_category": UserCategory.ACCOUNT_MANAGER,
    }

    await _request(callback=callback, bot=bot, state=state, data=data)


@client_router.callback_query(lambda c: c.data == "payment_request", StateFilter(ClientForm))
async def handle_payment_request(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    await callback.message.delete()
    # managers = await get_managers()
    # for i in managers:
    #     if i.category == UserCategory.EXECUTIVE_DIRECTOR and i.vacation_start < datetime.datetime.now() < i.vacation_end:
    #         await callback.message.answer(f"Нахожусь в отпуске с {i.vacation_start[0:9]} по {i.vacation_end[0:9]}, по вопросам взаиморасчетов свяжитесь, пожалуйста, с Юлией по тел. {i.number}.")

    user_id = callback.from_user.id
    username = callback.from_user.username or "Неизвестный пользователь"

    user_data = await state.get_data()
    contract_number_or_inn = user_data.get("contract_number_or_inn", "Не указано")

    message_text = f"Пользователь {username} (Номер договора/ИНН: {contract_number_or_inn}, ID: {user_id}) отправил запрос по теме 'Вопрос по взаиморасчётам'."

    data = {
        "message_text": message_text,
        "contact_number_or_inn": contract_number_or_inn,
        "user_id": user_id,
        "status": RequestCategory.PAYMENT,
        "user_category": UserCategory.EXECUTIVE_DIRECTOR,
    }

    await _request(callback=callback, bot=bot, state=state, data=data)