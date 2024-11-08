from aiogram import Bot, Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from fsm.client_fsm import ClientForm
from keyboards.inline.client_kb import request_categories_keyboard, accept_or_skip
from keyboards.inline.answer_kb import answer_keyboard
from logger import logger
from config import EXECUTIVE_DIRECTOR


client_router = Router(name="client")


@client_router.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext) -> None:
    # TODO сделать с 9 до 18 работу
    await message.answer("Добрый день! Для обработки запроса укажите номер договора или ИНН")
    await state.set_state(ClientForm.contract_number_or_inn)


@client_router.message(ClientForm.contract_number_or_inn)
async def proccess_contract_number_or_inn(message: types.Message, state: FSMContext) -> None:
    await state.update_data(contract_number_or_inn=message.text)
    await message.answer("Выберите, пожалуйста, категорию вашего запроса:", reply_markup=request_categories_keyboard())


        
# @client_router.callback_query(lambda c: c.data == "order_request")
# async def handle_order_request(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
#     user_data = await state.get_data()
#     contract_number_or_inn = user_data.get("contract_number_or_inn", "Не указано")
#     user_id = callback.from_user.id
#     username = callback.from_user.username or "Неизвестный пользователь"
#     message_text = f"Пользователь {username} (Номер договора/ИНН: {contract_number_or_inn}, ID: {user_id}) отправил запрос."

#     for manager_id in CLO_MANAGER:  # КЛО Менеджер
#         try:
#             await bot.send_message(manager_id, message_text, reply_markup=accept_or_skip())
#         except Exception as e:
#             logger.error(f"Не удалось отправить сообщение менеджеру {manager_id}: {e}")

#     await callback.message.answer("В течение 10 минут с вами свяжется первый освободившийся менеджер.")


@client_router.callback_query(lambda c: c.data == "payment_request")
async def handle_payment_request(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    user_id = callback.from_user.id
    username = callback.from_user.username or "Неизвестный пользователь"

    user_data = await state.get_data()
    contract_number_or_inn = user_data.get("contract_number_or_inn", "Не указано")

    message_text = f"Пользователь {username} (Номер договора/ИНН: {contract_number_or_inn}, ID: {user_id}) отправил запрос по взаиморасчетам."

    try:
        await bot.send_message(EXECUTIVE_DIRECTOR[0], text=message_text, reply_markup=answer_keyboard(user_id=user_id))
    except Exception as e:
        logger.error(f"Не удалось отправить сообщение менеджеру {EXECUTIVE_DIRECTOR[0]}: {e}")

    await callback.message.answer("В течение 10 минут с вами свяжется первый освободившийся менеджер.")



# @client_router.callback_query(lambda c: c.data == "account_request")
# async def handle_account_request(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
#     user_id = callback.from_user.id
#     username = callback.from_user.username or "Неизвестный пользователь"

#     user_data = await state.get_data()
#     contract_number_or_inn = user_data.get("contract_number_or_inn", "Не указано")

#     message_text = f"Пользователь {username} (Номер договора/ИНН: {contract_number_or_inn}, ID: {user_id}) отправил запрос по вопросу личного кабинета."

#     for manager_id in ACCOUNT_MANAGER:  # Менеджеры по сопровождению
#         try:
#             await bot.send_message(manager_id, message_text)
#         except Exception as e:
#             logger.error(f"Не удалось отправить сообщение менеджеру {manager_id}: {e}")

#     await callback.message.answer("В течение 10 минут с вами свяжется первый освободившийся менеджер.")

# @client_router.callback_query(lambda c: c.data == "other_request")
# async def handle_other_request(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
#     user_id = callback.from_user.id
#     username = callback.from_user.username or "Неизвестный пользователь"

#     user_data = await state.get_data()
#     contract_number_or_inn = user_data.get("contract_number_or_inn", "Не указано")

#     message_text = f"Пользователь {username} (Номер договора/ИНН: {contract_number_or_inn}, ID: {user_id}) отправил запрос на другой вопрос."

#     for manager_id in ACCOUNT_MANAGER:  # Менеджеры по сопровождению
#         try:
#             await bot.send_message(manager_id, message_text)
#         except Exception as e:
#             logger.error(f"Не удалось отправить сообщение менеджеру {manager_id}: {e}")

#     await callback.message.answer("В течение 10 минут с вами свяжется первый освободившийся менеджер.")


