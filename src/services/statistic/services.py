import asyncio
import datetime
from typing import Dict, Any

import gspread
from google.oauth2.credentials import Credentials
from logger.logger import setup_logger
from src.services.config.config import settings
from src.services.database.models import RequestSubCategory


class StatisticService:
    def __init__(self, logger=setup_logger(__name__)):
        self.logger = logger
        self.timeout = [30, 60]
        self.SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
        self.SPREADSHEET_ID = settings.get_manager_link
        self.month = {
            1: "Январь",
            2: "Февраль",
            3: "Март",
            4: "Апрель",
            5: "Май",
            6: "Июнь",
            7: "Июль",
            8: "Август",
            9: "Сентябрь",
            10: "Октябрь",
            11: "Ноябрь",
            12: "Декабрь",
        }

        self.data_in_google = {
            1: "A1:AG10",
            2: "A12:AG21",
            3: "A23:AG32",
            4: "A34:AG43",
            5: "A45:AG54",
            6: "A56:AG65",
            7: "A67:AG76",
            8: "A78:AG87",
            9: "A89:AG98",
            10: "A100:AG109",
            11: "A111:AG120",
            12: "A122:AG131",  # Исправлено на правильный диапазон
        }

        self.client = None
        self._conn = False
        self.error = 0

    async def start(self, field: str, subcategory: RequestSubCategory) -> None | Dict[str, Any]:
        try:
            await self._connect()
            await self._set_update(field=field,subcategory=subcategory)
        except Exception as e:
            if self.error == 2:
                return {
                    "status": 400,
                    "error": str(e),
                    "text": "Не удалось записать в статистику",
                }

            self.logger.error(e)
            self.error += 1
            await asyncio.sleep(self.timeout[1])
            await self.start(field, subcategory)

    async def _connect(self):
        try:
            creds = Credentials.from_authorized_user_file("./input_api/token.json", scopes=self.SCOPES)
            self.client = gspread.authorize(creds)
            self._conn = True
            return self.client
        except Exception as e:
            self.logger.error(e)
            await asyncio.sleep(self.timeout[0])

    async def _get_month(self):
        today_month = datetime.datetime.now().month
        today = datetime.datetime.now().day
        return {
            "date": self.month.get(today_month),
            "date_number": today_month,
            "day": today,
        }

    async def _set_update(self, field: str, subcategory: RequestSubCategory):
        if not self._conn:
            self.logger.debug(self._conn)
            return {
                "status": 404,
                "text": "Авторизация не произошла",
                "error": self._conn,
            }

        try:
            sheet = self.client.open_by_key(self.SPREADSHEET_ID)
            today_month = await self._get_month()
            worksheet = sheet.worksheet(field)
            range_name = self.data_in_google.get(today_month['date_number'])

            values_list = worksheet.batch_get([range_name])[0]
            self.logger.debug(values_list[0])
            self.logger.debug(f"Диапазон данных для месяца {today_month['date']}: {range_name}")

            # Найти строку, соответствующую текущему месяцу
            month_row_index = None
            for i, row in enumerate(values_list):
                self.logger.debug(row[0].split('/')[-1].strip())
                self.logger.debug(today_month['date'].lower())
                if row[0].split('/')[-1].strip() == today_month['date'].lower():
                    month_row_index = i + int(range_name.split(":")[0].replace("A", ""))  # +1, потому что индексы в Google Sheets начинаются с 1
                    break

            if month_row_index is None:
                self.logger.error(f"Строка для месяца {today_month['date']} не найдена")
                return

            self.logger.debug(f"Найдена строка для месяца {today_month['date']} на позиции {month_row_index}")

            # Найти строку, соответствующую нужной категории
            category_row_index = None
            for i, row in enumerate(values_list):
                if row[0].strip().lower() == subcategory.value.lower():
                    self.logger.debug(i)
                    category_row_index = i + int(range_name.split(":")[0].replace("A", ""))  # +1, потому что индексы в Google Sheets начинаются с 1
                    break

            if category_row_index is None:
                self.logger.error(f"Строка для категории {subcategory} не найдена")
                return

            self.logger.debug(f"Найдена строка для категории {subcategory} на позиции {category_row_index}")

            # Обновить значение в нужной ячейке
            day_column_index = today_month['day'] + 2  # +2, потому что первые две колонки - это заголовок и "Итого"
            current_value = worksheet.cell(category_row_index, day_column_index).value
            new_value = int(current_value) + 1 if current_value else 1
            worksheet.update_cell(category_row_index, day_column_index, new_value)

            self.logger.debug(f"Обновлено значение для категории {subcategory}, день {today_month['day']}: {new_value}")

        except Exception as e:
            self.logger.error(e)