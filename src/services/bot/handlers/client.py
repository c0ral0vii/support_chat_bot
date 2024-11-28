import asyncio
import time

from aiogram import Bot, Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, StateFilter
from aiogram.exceptions import TelegramBadRequest
from logger.logger import setup_logger
from src.services.database.models import UserCategory, RequestCategory, Request
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
client_router = Router(name="client")

logger = setup_logger(__name__)


@client_router.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext) -> None:
    # try:
    #     user_id = message.from_user.id
    #     manager = await get_manager(user_id=user_id)
    #
    #     if manager:
    #         if manager.category == UserCategory.EXECUTIVE_DIRECTOR:
    #             await message.answer("Вы вступили в пост 'Исполнительный директор'.", reply_markup=executive_director_kb.executive_director_keyboards())
    #             return
    #         if manager.category == UserCategory.SENIOR_CLO_MANAGER:
    #             await message.answer("Вы вступили в пост 'Старший менеджер КЛО'.", reply_markup=senior_clo_manager.senior_clo_manager())
    #             return
    #         if manager.category == UserCategory.CLO_MANAGER:
    #             await message.answer("Вы вступили на пост 'Менеджеры КЛО'.")
    #             return
    #         if manager.category == UserCategory.ACCOUNT_MANAGER:
    #             await message.answer("Вы вступили на пост 'Менеджеры по сопровождению'.")
    #             return

    # if 9 < int(time.strftime('%H')) < 18: # TODO включить при пуше
    await create_user({
        "user_id": int(message.from_user.id),
        "username": message.from_user.username,
    })
    await message.answer(
        "Добрый день, режим работы с 9:00 до 19:00 МСК!\nДля обработки запроса укажите номер договора или ИНН")
    await state.clear()
    await state.set_state(ClientForm.contract_number_or_inn)
    # else:
    #     await message.answer("Ой, все уже ушли домой, как только вернемся на работу, обязательно вам ответим")



@client_router.message(ClientForm.contract_number_or_inn)
async def proccess_contract_number_or_inn(message: types.Message, state: FSMContext) -> None:
    await state.update_data(contract_number_or_inn=message.text)

    await message.answer("Выберите, пожалуйста, категорию вашего запроса:", reply_markup=request_categories_keyboard())


async def _request(callback: types.CallbackQuery, bot: Bot, state: FSMContext, data: dict):
    managers = await get_managers()

    await callback.message.answer("В течение 10 минут с вами свяжется первый освободившийся менеджер.")

    messages = []
    logger.debug(data)
    request = await create_request(data=data)

    for i in managers:
        try:
            if type(data["user_category"]) == list:
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
    logger.debug("разослали все сообщения")


    asyncio.create_task(_create_notification(messages=messages, bot=bot, data=data, managers=managers, request=request, max_interval=data["max_interval"]))


async def _create_notification(messages: list[types.Message], bot: Bot, data: dict, managers: list, request: Request, max_interval: int = 999) -> None:
    interval = 0
    while True:
        await asyncio.sleep(60)

        check_request = await get_request(request_id=request.id)
        if check_request["request_manager"] or check_request["request_status"]:
            await delete_message(messages)
            break

        if interval == max_interval:
            if max_interval != 30:
                data["max_interval"] = 30
                new_message = f"!!->Просрочен---{data["message_text"]}---Просрочен<-!!"
                data["message_text"] = new_message
                data["user_category"] = [UserCategory.SENIOR_CLO_MANAGER, UserCategory.ACCOUNT_MANAGER]
                asyncio.create_task(_create_notification(messages, bot, data, managers, request, max_interval))

            if max_interval == 30:
                await bot.send_message(chat_id=data["user_id"], text="Вы можете связаться со своим закрепленным менеджером.")
                break
            break

        interval += 1

        for i in managers:
            try:
                logger.debug(interval)
                if not data["user_category"] is None:
                    if i.category == data['user_category'] and i.free:
                        message = await bot.send_message(chat_id=i.user_id, text=data["message_text"],
                                                         reply_markup=answer_keyboard(request_id=request.id))
                        messages.append(message)


                if type(data["user_category"]) == list:
                    for user_category in data["user_category"]:
                        if i.category == user_category:
                            message = await bot.send_message(chat_id=i.user_id, text=data["message_text"],
                                                             reply_markup=answer_keyboard(request_id=request.id))
                            messages.append(message)
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

    message_text = f"Пользователь {username} (Номер договора/ИНН: {contract_number_or_inn}, ID: {user_id}) отправил запрос по взаиморасчетам."

    data = {
        "message_text": message_text,
        "contact_number_or_inn": contract_number_or_inn,
        "user_id": user_id,
        "status": RequestCategory.ORDER,
        "user_category": UserCategory.CLO_MANAGER,
        "max_interval": 10,
    }

    await _request(callback=callback, bot=bot, state=state, data=data)


@client_router.callback_query(lambda c: c.data == "account_request", StateFilter(ClientForm))
async def handle_account_request(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    await callback.message.delete()

    user_id = callback.from_user.id
    username = callback.from_user.username or "Неизвестный пользователь"

    user_data = await state.get_data()
    contract_number_or_inn = user_data.get("contract_number_or_inn", "Не указано")

    message_text = f"Пользователь {username} (Номер договора/ИНН: {contract_number_or_inn}, ID: {user_id}) отправил запрос по взаиморасчетам."

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

    message_text = f"Пользователь {username} (Номер договора/ИНН: {contract_number_or_inn}, ID: {user_id}) отправил запрос по взаиморасчетам."

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

    user_id = callback.from_user.id
    username = callback.from_user.username or "Неизвестный пользователь"

    user_data = await state.get_data()
    contract_number_or_inn = user_data.get("contract_number_or_inn", "Не указано")

    message_text = f"Пользователь {username} (Номер договора/ИНН: {contract_number_or_inn}, ID: {user_id}) отправил запрос по взаиморасчетам."

    data = {
        "message_text": message_text,
        "contact_number_or_inn": contract_number_or_inn,
        "user_id": user_id,
        "status": RequestCategory.PAYMENT,
        "user_category": UserCategory.EXECUTIVE_DIRECTOR,
    }

    await _request(callback=callback, bot=bot, state=state, data=data)





