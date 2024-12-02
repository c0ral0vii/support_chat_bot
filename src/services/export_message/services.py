import pandas as pd
from aiogram import Bot
from aiogram.types import FSInputFile

from logger.logger import setup_logger


from src.services.database.orm.get_messages import get_messages


class ExportMessageService:
    def __init__(self,
                 logger=setup_logger(__name__),):
        self.logger = logger


    async def export_messages(self, request_id, bot: Bot, user_id: int):
        messages = await get_messages(request_id=request_id)


        df = pd.DataFrame([{
            "От кого": message.from_,
            "Сообщение": message.message,
            "Отправлено": message.created,
        } for message in messages])

        excel_file = f"./temp/dialog_files/dialog_{str(request_id)}.xlsx"
        df.to_excel(excel_file, index=False)

        self.logger.debug(f"Exported messages to {excel_file}")

        file = FSInputFile(excel_file)
        await bot.send_document(chat_id=user_id, document=file)

        return {
            "status": 200,
            "file": excel_file,
            "text": "Успешно создан",
        }
