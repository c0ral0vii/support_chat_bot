from aiogram import Router, F, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton

from logger.logger import setup_logger
from src.services.bot.fsm.client_fsm import VacationForm
from src.services.database.orm.managers import set_vacation, get_manager, disable_vacation

vacation_router = Router(name='vacation_router')
logger = setup_logger(__name__)


@vacation_router.message(F.text == "Установить автоответ")
async def vacation_set(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(VacationForm.from_)
    manager = await get_manager(user_id=message.from_user.id)

    if manager.vacation_start:
        manager_text = f"Вот ваш автоответ, если нужно удалить или поменять сначала удалите его кнопкой снизу:\n\nНахожусь в отпуске с {manager.vacation_start} по {manager.vacation_end}, по вопросам взаиморасчетов свяжитесь, пожалуйста, с Юлией по тел. {manager.number}."
        await message.answer(manager_text, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Удалить напоминание", callback_data="disable_vacation")],
        ]))
        return

    await message.answer(VacationForm.texts["VacationForm:from_"])


@vacation_router.callback_query(F.data == "disable_vacation")
async def vacation_disavble(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()

    await disable_vacation(user_id=callback.from_user.id)

    await callback.message.answer("Автоответ удален")

@vacation_router.message(F.text, StateFilter(VacationForm.from_))
async def vacation_from(message: types.Message, state: FSMContext):
    await state.update_data(from_=message.text)
    await state.set_state(VacationForm.to_)

    await message.answer(VacationForm.texts["VacationForm:to_"])


@vacation_router.message(F.text, StateFilter(VacationForm.to_))
async def vacation_to(message: types.Message, state: FSMContext):
    await state.update_data(to_=message.text)
    await state.set_state(VacationForm.phone)
    await message.answer(VacationForm.texts["VacationForm:phone"])


@vacation_router.message(F.text, StateFilter(VacationForm.phone))
async def vacation_from_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    data = await state.get_data()
    phone = data["phone"]
    from_ = data["from_"]
    to_ = data["to_"]

    await set_vacation(user_id=message.from_user.id, data={
        "phone": phone,
        "from_": from_,
        "to_": to_
    })
    await message.answer(f"Вы установили автоответ на время от {from_} до {to_}, номер телефона для связи: {phone}")

    await state.clear()