from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext

from src.services.bot.fsm.messages_fsm import MessageForm
from src.services.database.orm.create_request import get_request
from src.services.database.orm.managers import get_manager

message_router = Router(name='message_router')


@message_router.callback_query(lambda query: query.data == 'start_chat_')
async def send_message(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    user_id = callback.from_user.id

    request = await get_request(request_id=int(callback.data.split("_")[-1]))

    manager = await get_manager(user_id=user_id)

    if manager.get("error"):
        if request.close == True:
            await callback.message.answer("Ваше обращение закрыто, если остались вопросы создайте ещё одно обращение")
            await state.clear()
            return

        await state.set_state(MessageForm.text)


    else:
        await state.set_state(MessageForm.text)

        await callback.message.answer("Напишите ваш ответ или отправьте файл:")