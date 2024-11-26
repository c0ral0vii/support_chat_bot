from aiogram import types, Router, F

from src.services.database.models import RequestSubCategory
from src.services.database.orm.create_request import change_subcategory

subcategory_router = Router(name='subcategory_router')


@subcategory_router.callback_query(lambda query: "subcategory_" in query.data)
async def create_subcategory(callback: types.CallbackQuery):
    subcategory_data = callback.data.split("_")
    subcategory = RequestSubCategory.CUSTOM_SUBCATEGORY

    if subcategory_data[1] == "1":
        subcategory = RequestSubCategory.RESET_NP_AND_CHANGE_PAYER

    if subcategory_data[1] == "2":
        subcategory = RequestSubCategory.CREATE_INVOICE_OR_REQUEST

    if subcategory_data[1] == "3":
        subcategory = RequestSubCategory.CHANGE_RECIPIENT_CONTACTS

    if subcategory_data[1] == "4":
        subcategory = RequestSubCategory.CHANGE_DELIVERY_MODE_OR_PICKUP

    if subcategory_data[1] == "5":
        subcategory = RequestSubCategory.ORDER_FORWARDING

    if subcategory_data[1] == "6":
        subcategory = RequestSubCategory.CARGO_SEARCH

    if subcategory_data[1] == "7":
        subcategory = RequestSubCategory.CONSULTATION_ON_TS_AND_DELIVERY

    if subcategory_data[1] == "8":
        subcategory = RequestSubCategory.PROVIDE_DOCUMENTS

    await change_subcategory(request_id=int(subcategory_data[-1]), subcategory=subcategory)

    await callback.message.answer("Готово!")
