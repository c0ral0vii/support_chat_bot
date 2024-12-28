import asyncio

from aiogram import types, Router, F

from src.services.database.models import RequestSubCategory
from src.services.database.orm.create_request import change_subcategory, get_request
from src.services.database.orm.managers import get_manager
from src.services.statistic.services import StatisticService

subcategory_router = Router(name='subcategory_router')


@subcategory_router.callback_query(lambda query: "subcategory_" in query.data)
async def create_subcategory(callback: types.CallbackQuery):
    subcategory_data = callback.data.split("_")
    subcategory = RequestSubCategory.CUSTOM_SUBCATEGORY

    if subcategory_data[1] == "1":
        subcategory = RequestSubCategory.RESET_NP_AND_CHANGE_PAYER

    elif subcategory_data[1] == "2":
        subcategory = RequestSubCategory.CREATE_INVOICE_OR_REQUEST

    elif subcategory_data[1] == "3":
        subcategory = RequestSubCategory.CHANGE_RECIPIENT_CONTACTS

    elif subcategory_data[1] == "4":
        subcategory = RequestSubCategory.CHANGE_DELIVERY_MODE_OR_PICKUP

    elif subcategory_data[1] == "5":
        subcategory = RequestSubCategory.ORDER_FORWARDING

    elif subcategory_data[1] == "6":
        subcategory = RequestSubCategory.CARGO_SEARCH

    elif subcategory_data[1] == "7":
        subcategory = RequestSubCategory.CONSULTATION_ON_TS_AND_DELIVERY

    elif subcategory_data[1] == "8":
        subcategory = RequestSubCategory.PROVIDE_DOCUMENTS

    elif subcategory_data[1] == "10":
        subcategory = RequestSubCategory.ERROR_REQUEST

    await callback.message.edit_text("Подкатегория выбрана, заказ закрыт!")

    manager = await get_manager(user_id=int(callback.from_user.id))
    # request_model = await get_request(request_id=int(subcategory_data[-1]), full_model=True)

    if subcategory_data[1] != "10":
        stats = asyncio.create_task(StatisticService().start(
            field=str(manager.field),
            subcategory=subcategory,
        ))

    await change_subcategory(request_id=int(subcategory_data[-1]), subcategory=subcategory)

