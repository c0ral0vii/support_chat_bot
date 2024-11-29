from aiogram import Router, types, Bot
from aiogram.fsm.context import FSMContext

from src.services.database.orm.ratings import set_rating

rating_router = Router(name='rating_router')


@rating_router.callback_query(lambda query: 'rating_' in query.data)
async def rating_handler(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    rating_data = callback.data.split("_")

    await set_rating(rating=int(rating_data[-2]), request_id=int(rating_data[-1]))
    if 3 <= int(rating_data[-2]):
        await callback.message.edit_text("Спасибо за ваш отзыв, ваш отзыв очень важен для нас!\nЕсли у вас остались вопросы создайте ещё один запрос!")
    else:
        await callback.message.edit_text("Приносим наши извинения, ваш отзыв очень важен для нас!\nЕсли остались вопросы создайте ещё один запрос!")

    await state.clear()