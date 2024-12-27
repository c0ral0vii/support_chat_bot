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


import asyncio
from aiogram import Bot, types
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from typing import List, Dict

async def _create_notification(messages: List[types.Message], bot: Bot, data: Dict, managers: List, request: Request, max_interval: int = 999) -> None:
    interval = 0
    data["_a"] = False
    data["send"] = False

    while True:
        try:
            await asyncio.sleep(60)  # Пауза между итерациями
            interval += 1
            logger.debug(f"Рассылка, {interval} -- {data}")

            # Проверка статуса запроса
            check_request = await get_request(request_id=request.id)
            logger.debug(check_request)
            if not check_request:
                logger.warning("Запрос не найден")
                logger.debug("check")
                continue
            logger.debug("1")

            # Проверка времени (работаем только с 9 до 19)
            # time = await get_time()
            # if 9 < time.hour < 19:
            #     logger.debug("time")
            #     await asyncio.sleep(3600)  # Пауза на час, если время вне рабочего диапазона
            #     continue
            logger.debug("2")

            # Условия завершения цикла
            if check_request["request_manager"] or check_request["request_status"] is True or interval > max_interval:
                logger.debug("Тута")
                await delete_message(messages)
                return

            logger.debug("3")

            # Обработка просроченных запросов
            if interval >= 5 and data.get("status") == RequestCategory.ORDER and data["send"] is False:
                logger.debug(f"Просрочено, {data}")
                data["max_interval"] = 30

                if data["_a"] == False:
                    data["message_text"] = f"!!->Просрочен---{data['message_text']}---Просрочен<-!!"
                data["_a"] = True

                data["user_category"] = [UserCategory.ACCOUNT_MANAGER]
                for i in managers:
                    try:
                        if not data["user_category"]:
                            continue

                        # Если user_category — это список
                        if isinstance(data["user_category"], list):
                            for user_category in data["user_category"]:
                                try:
                                    if i.category == user_category and i.user_id not in skip_user_id and i.free:
                                        message = await bot.send_message(
                                            chat_id=i.user_id,
                                            text=data["message_text"],
                                            reply_markup=answer_keyboard(request_id=request.id)
                                        )
                                        messages.append(message)
                                except (TelegramBadRequest, TelegramForbiddenError) as e:
                                    logger.warning(f"Ошибка отправки сообщения пользователю {i.user_id}: {e}")
                                    skip_user_id.add(i.user_id)  # Добавляем ID пользователя в множество skip_user_id
                                except Exception as e:
                                    logger.warning(f"Неизвестная ошибка: {e}")
                                    continue
                    except Exception as e:
                        logger.error(f"Критическая ошибка в цикле: {e}")
                        continue
                data["send"] = True

            logger.debug("3")

            # Уведомление пользователя при достижении максимального интервала
            if max_interval == 30 and interval == 30:
                logger.debug("inter")

                await bot.send_message(chat_id=data["user_id"], text="Вы можете связаться со своим закрепленным менеджером.")
                return

            logger.debug("4")

            # Отправка сообщений менеджерам
            skip_user_id = set()  # Множество для хранения ID пользователей, которым отправка не удалась
            for i in managers:
                try:
                    if not data["user_category"]:
                        continue

                    # Если user_category — это список
                    if isinstance(data["user_category"], list):
                        for user_category in data["user_category"]:
                            try:
                                if i.category == user_category and i.user_id not in skip_user_id and i.free:
                                    message = await bot.send_message(
                                        chat_id=i.user_id,
                                        text=data["message_text"],
                                        reply_markup=answer_keyboard(request_id=request.id)
                                    )
                                    messages.append(message)
                            except (TelegramBadRequest, TelegramForbiddenError) as e:
                                logger.warning(f"Ошибка отправки сообщения пользователю {i.user_id}: {e}")
                                skip_user_id.add(i.user_id)  # Добавляем ID пользователя в множество skip_user_id
                            except Exception as e:
                                logger.warning(f"Неизвестная ошибка: {e}")
                                continue

                    # Если user_category — это одно значение
                    else:
                        try:
                            if i.category == data["user_category"] and i.user_id not in skip_user_id and i.free:
                                message = await bot.send_message(
                                    chat_id=i.user_id,
                                    text=data["message_text"],
                                    reply_markup=answer_keyboard(request_id=request.id)
                                )
                                messages.append(message)
                        except (TelegramBadRequest, TelegramForbiddenError) as e:
                            logger.warning(f"Ошибка отправки сообщения пользователю {i.user_id}: {e}")
                            skip_user_id.add(i.user_id)  # Добавляем ID пользователя в множество skip_user_id
                        except Exception as e:
                            logger.warning(f"Неизвестная ошибка: {e}")
                            continue

                except Exception as e:
                    logger.warning(f"Ошибка при обработке менеджера {i.user_id}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Критическая ошибка в цикле: {e}")
            continue


async def delete_message(messages):
    for message in messages:
        try:
            await message.delete()
        except:
            continue


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
        "user_category": [UserCategory.CLO_MANAGER],
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
    managers = await get_managers()

    # Assuming `managers` is a list of database model instances
    for i in managers:
        if i.category == UserCategory.EXECUTIVE_DIRECTOR and i.vacation_start and i.vacation_end:
            from datetime import datetime
            now = datetime.now()
            if i.vacation_start <= now <= i.vacation_end:
                # Format the dates properly
                vacation_start_str = i.vacation_start.strftime("%d.%m.%Y")
                vacation_end_str = i.vacation_end.strftime("%d.%m.%Y")
                await callback.message.answer(
                    f"Нахожусь в отпуске с {vacation_start_str} по {vacation_end_str}, "
                    f"по вопросам взаиморасчетов свяжитесь, пожалуйста, с Юлией по тел. {i.number}."
                )
                return

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