from aiogram import Bot, Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from fsm.client_fsm import ClientForm

client_router = Router(name="client")


@client_router.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext) -> None:
    await message.answer("Добрый день! Для обработки запроса укажите номер договора или ИНН")
    await state.set_state(ClientForm.contract_number_or_inn)

@client_router.message(ClientForm.contract_number_or_inn)
async def proccess_contract_number_or_inn(message: types.Message, state: FSMContext) -> None:
    await state.update_data(contract_number_or_inn=message.text)
    await message.answer("Выберите, пожалуйста, категорию вашего запроса:", reply_markup=request_categories_keyboard())




@client_router.callback_query(lambda c: c.data == "payment_request")
async def handle_payment_request(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    user_id = callback.from_user.id
    username = callback.from_user.username or "Неизвестный пользователь"

    user_data = await state.get_data()
    contract_number_or_inn = user_data.get("contract_number_or_inn", "Не указано")

    message_text = f"Пользователь {username} (Номер договора/ИНН: {contract_number_or_inn}, ID: {user_id}) отправил запрос по взаиморасчетам."

        try:
        except Exception as e:

    await callback.message.answer("В течение 10 минут с вами свяжется первый освободившийся менеджер.")












