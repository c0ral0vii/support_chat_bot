from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from more_itertools import chunked

from logger.logger import setup_logger
from src.services.bot.keyboards.inline.detail_request import detail_request
from src.services.bot.keyboards.inline.pagination_kb import pagination_kb
from src.services.database.models import UserCategory
from src.services.database.orm.create_request import get_requests, get_request
from src.services.database.orm.managers import get_manager

executive_director_router = Router(name='Executive director')
logger = setup_logger(__name__)


@executive_director_router.message(F.text == 'Получить все запросы')
async def get_all_requests(message: types.Message, bot: Bot, state: FSMContext):

    await state.clear()

    manager = await get_manager(user_id=message.from_user.id)
    if not manager:
        return

    if manager.category == UserCategory.SENIOR_CLO_MANAGER:
        requests = await get_requests(CLO=True)
        await state.update_data(clo=True)
    if manager.category in [UserCategory.EXECUTIVE_DIRECTOR, UserCategory.ACCOUNT_MANAGER]:
        requests = await get_requests()

    try:        
        chunks = list(chunked(requests, 5))
    except:
        await message.answer("У нас пока нет заявок")
        return
    
    await state.update_data(page=1, max_pages=len(chunks), pagesll=chunks)

    logger.debug(requests)
    await message.answer('Все заявки:', reply_markup=await pagination_kb(page=1, list_requests=chunks[0], max_page=len(chunks)))


@executive_director_router.callback_query(lambda c: "detail_" in c.data)
async def detail(callback: types.CallbackQuery, state: FSMContext):
    data = callback.data.split("_")[-1]
    request_data = await get_request(request_id=int(data), full_model=True)

    await callback.message.answer(f"Запрос - {request_data.id}:\nЗакрыт: {"✅" if request_data.close else '❌'}\nИНН: {request_data.contact_number_or_inn}\nМенеджер принявший: {request_data.manager_id}\nПользователь: {request_data.user_id}\nКатегория: {request_data.request_category.value}\nПодкатегория: {request_data.subcategory.value}\n\nСоздан: {request_data.created}\nПоследнее обновление: {request_data.updated}",
                                  reply_markup=await detail_request(request_id=int(request_data.id)))


@executive_director_router.callback_query(lambda c: c.data == "refresh")
async def refresh(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    data = await state.get_data()
    page = data["page"]
    clo = data.get("clo")
    if clo:
        requests = await get_requests(CLO=True)
    else:
        requests = await get_requests()

    chunks = list(chunked(requests, 5))

    await state.update_data(page=page, max_pages=len(chunks), pages=chunks)
    await callback.message.delete()
    await callback.message.answer(text="Все заявки:", reply_markup=await pagination_kb(page=page, max_page=len(chunks),
                                                                                          list_requests=chunks[page - 1]))

@executive_director_router.callback_query(lambda c: c.data == "right_pagination")
async def to_right(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    data = await state.get_data()
    logger.debug(data)
    page = data['page']
    pages = data['pages']
    max_pages = data['max_pages']

    if max_pages <= page:
        logger.debug(max_pages)
        return

    page += 1
    await state.update_data(page=page)
    await callback.message.edit_text(text="Все заявки:", reply_markup=await pagination_kb(page=page, max_page=max_pages, list_requests=pages[page-1]))


@executive_director_router.callback_query(lambda c: c.data == 'left_pagination')
async def to_left(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    data = await state.get_data()
    page = data['page']
    pages = data['pages']
    max_pages = data['max_pages']

    if 1 == page:
        return

    page -= 1
    await state.update_data(page=page)
    await callback.message.edit_text(text="Все заявки:", reply_markup=await pagination_kb(page=page, max_page=max_pages, list_requests=pages[page-1]))
