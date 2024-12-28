from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_subcategory_markup(request_id: int):
    first_button = InlineKeyboardButton(text="1. Заявка на обнуление НП и смену плательщика", callback_data=f"subcategory_1_{request_id}")
    second_button = InlineKeyboardButton(text="2. Создание накладной/заявки", callback_data=f"subcategory_2_{request_id}")
    three_button = InlineKeyboardButton(text="3. Смена контактных данных получателя", callback_data=f"subcategory_3_{request_id}")
    four_button = InlineKeyboardButton(text="4. Смена режима доставки, смена ПВЗ", callback_data=f"subcategory_4_{request_id}")
    five_button = InlineKeyboardButton(text="5. Пересыл заказа", callback_data=f"subcategory_5_{request_id}")
    six_button = InlineKeyboardButton(text="6. Поиск груза", callback_data=f"subcategory_6_{request_id}")
    seven_button = InlineKeyboardButton(text="7. Консультация по ТС и срокам доставки", callback_data=f"subcategory_7_{request_id}")
    eight_button = InlineKeyboardButton(text="8. Предоставление документов, подтверждающих доставку/отправку", callback_data=f"subcategory_8_{request_id}")
    nine_button = InlineKeyboardButton(text="9. Свой вариант подкатегории запроса (возможность написать)", callback_data=f"subcategory_9_{request_id}")
    error_button = InlineKeyboardButton(text="10. Ошибочный запрос, клиент относится к другому юр. лицу", callback_data=f"subcategory_10_{request_id}")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [first_button],
        [second_button],
        [three_button],
        [four_button],
        [five_button],
        [six_button],
        [seven_button],
        [eight_button],
        [nine_button],
        [error_button],
    ])

    return keyboard