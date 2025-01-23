from aiogram import Router, F, types, Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from src.services.bot.fsm.messages_fsm import MessageForm
from src.services.bot.keyboards.inline.answer_kb import answer_client_keyboard, answer_manager_keyboard
from src.services.database.database import logger
from src.services.database.orm.create_request import get_request
from src.services.database.orm.managers import get_manager
from src.services.database.orm.messages import create_message

message_router = Router(name='message_router')


@message_router.callback_query(lambda query: "send_message_" in query.data)
async def start_chat(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    await state.clear()

    user_id = callback.from_user.id
    manager = await get_manager(user_id=user_id)
    logger.debug(callback.data)
    request = await get_request(request_id=int(callback.data.split("_")[-2]), full_model=True)

    await state.update_data(from_=callback.from_user.id)

    if isinstance(manager, dict):
        if request.close == True:
            await callback.message.answer("Ваше обращение закрыто, если остались вопросы создайте ещё одно обращение")
            await state.clear()
            return

        await state.set_state(MessageForm.text)
        await state.update_data(to=request.manager_id, request_id=int(callback.data.split("_")[-2]), inn=request.contact_number_or_inn)

        await callback.message.answer("Постарайтесь описать всё в одном сообщении если это возможно\n\n\nНапишите ваш вопрос:")

    else:
        await state.set_state(MessageForm.text)

        await state.update_data(to=request.user_id, request_id=int(callback.data.split("_")[-2]))
        await callback.message.answer(f"Вы пишите по {request.id}->{request.user_id}\n\n\nНапишите ваш ответ:")


@message_router.message(F.text, StateFilter(MessageForm.text))
async def send_message(message: types.Message, bot: Bot, state: FSMContext):
    user_id = message.from_user.id
    manager = await get_manager(user_id=user_id)

    await state.update_data(text=message.text)
    data = await state.get_data()

    await create_message(data={
        "from": data["from_"],
        "request_id": data["request_id"],
        "message": data["text"],
    })

    if data["to"] is None:
        await message.answer("Ожидайте ответ оператора.")

    if isinstance(manager, dict):
        #менеджеру
        await bot.send_message(chat_id=data["to"], text=f'ИНН: {data["inn"]}\n\n{data["text"]}', reply_markup=answer_manager_keyboard(request_id=data["request_id"], user_id=data["to"]))
        #пользователю
        await message.answer("Ожидайте ответ оператора.", reply_markup=await answer_client_keyboard(user_id=data["to"], request_id=data["request_id"]))
        # await state.clear()
    else:
        #пользователю
        try:
            await bot.send_message(chat_id=data["to"], text=data["text"], reply_markup=await answer_client_keyboard(request_id=data["request_id"], user_id=data["to"]))
            #менеджеру
            await message.answer(f"Ваше сообщение отправлено.\n\n\nЧтобы продолжить диалог нажмите кнопку 'Отправить сообщение'", reply_markup=answer_manager_keyboard(request_id=data["request_id"], user_id=data["to"]))
            # await state.clear()
        except TelegramForbiddenError as te:
            logger.warning(te)
            await message.answer(f"❗ Произошла ошибка ❗\n\n⚠️Возможно пользователь заблокировал бота или удален, но вы можете попробовать еще раз отправить сообщение ему.", reply_markup=answer_manager_keyboard(request_id=data["request_id"], user_id=data["to"]))
            await state.clear()
        except Exception as e:
            logger.warning(e)
            await message.answer(f"❗ Произошла ошибка ❗\n\n⚠️Возможно пользователь заблокировал бота или удален, но вы можете попробовать еще раз отправить сообщение ему.", reply_markup=answer_manager_keyboard(request_id=data["request_id"], user_id=data["to"]))
            await state.clear()


@message_router.message(F.content_type.in_({'document', 'photo'}), StateFilter(MessageForm.text))
async def send_media(message: types.Message, bot: Bot, state: FSMContext):
    user_id = message.from_user.id
    manager = await get_manager(user_id=user_id)

    if message.content_type == 'document':
        file_id = message.document.file_id
    elif message.content_type == 'photo':
        file_id = message.photo[-1].file_id  # Берем последний элемент, так как он имеет наибольшее разрешение

    file_info = await bot.get_file(file_id)
    file_path = file_info.file_path

    await state.update_data(file_id=file_id, file_path=file_path)
    data = await state.get_data()

    await create_message(data={
        "from": data["from_"],
        "request_id": data["request_id"],
        "message": "Отправлен медиафайл",
    })

    if isinstance(manager, dict):
        if message.content_type == 'document':
            await bot.send_document(chat_id=data["to"], document=file_id, reply_markup=answer_manager_keyboard(request_id=data["request_id"], user_id=data["to"]))
        elif message.content_type == 'photo':
            await bot.send_photo(chat_id=data["to"], photo=file_id, reply_markup=answer_manager_keyboard(request_id=data["request_id"], user_id=data["to"]))

        await message.answer("Ожидайте ответ оператора.", reply_markup=await answer_client_keyboard(user_id=data["to"], request_id=data["request_id"]))
        # await state.clear()
    else:
        if message.content_type == 'document':
            await bot.send_document(chat_id=data["to"], document=file_id, reply_markup=await answer_client_keyboard(request_id=data["request_id"], user_id=data["to"]))
        elif message.content_type == 'photo':
            await bot.send_photo(chat_id=data["to"], photo=file_id, reply_markup=await answer_client_keyboard(request_id=data["request_id"], user_id=data["to"]))

        await message.answer(f"Ваш медиафайл отправлен.\n\n\nЧтобы продолжить диалог нажмите кнопку 'Отправить сообщение'", reply_markup=answer_manager_keyboard(request_id=data["request_id"], user_id=data["to"]))
        # await state.clear()