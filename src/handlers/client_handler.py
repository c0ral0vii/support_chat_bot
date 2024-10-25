from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from fsm.client_fsm import ClientForm
from keyboards.inline.request_categories import request_categories_keyboard

client_router = Router(name="client")


@client_router.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext) -> None:
    await message.answer("Добрый день! Для обработки запроса укажите номер договора или ИНН")
    await state.set_state(ClientForm.contract_number_or_inn)

@client_router.message(ClientForm.contract_number_or_inn)
async def proccess_contract_number_or_inn(message: types.Message, state: FSMContext) -> None:
    await message.answer("Выберите, пожалуйста, категорию вашего запроса:", reply_markup=request_categories_keyboard())

@client_router.callback_query(lambda c: c.data == "order_request")
async def handle_order_request(callback: types.CallbackQuery):
    await callback.message.answer("В течение 10 минут с вами свяжется первый освободившийся менеджер")

@client_router.callback_query(lambda c: c.data == "payment_request")
async def handle_payment_request(callback: types.CallbackQuery):
    await callback.message.answer("В течение 10 минут с вами свяжется первый освободившийся менеджер")

@client_router.callback_query(lambda c: c.data == "account_request")
async def handle_account_request(callback: types.CallbackQuery):
    await callback.message.answer("В течение 10 минут с вами свяжется первый освободившийся менеджер")

@client_router.callback_query(lambda c: c.data == "other_request")
async def handle_other_request(callback: types.CallbackQuery):
    await callback.message.answer("В течение 10 минут с вами свяжется первый освободившийся менеджер")


