from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from keyboards.inline.answer_kb import answer_client_keyboard, answer_manager_keyboard
from logger import logger


executive_director = Router(name='Executive director')


@executive_director.callback_query(lambda c: 'start_chat_' in c.data)
async def start_chat(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    message = f'Ваш запрос был принят менеджером скоро с вами свяжуться'
    try:
        user_id = int(callback.data.split('_')[-1])
        await bot.send_message(user_id, text=message)
    
        await callback.message.answer('Отправьте сообщение пользователю', reply_markup=answer_manager_keyboard(user_id=user_id))
    except Exception as e:
        logger.error('Возникла ошибка при отправке сообщения')
