import re
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from src.logger import logger

creds = Credentials.from_service_account_file('src/utils/data/creds.json')
scoped_creds = creds.with_scopes([
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
])
client = gspread.authorize(scoped_creds)

def load_managers_ids():
    managers = {
        'CLO_MANAGER': [],
        'SENIOR_CLO_MANAGER': [],
        'ACCOUNT_MANAGER': [],
        'EXECUTIVE_DIRECTOR': []
    }

    try:
        spreadsheet_id = '1jY-6h7R05p6BG617_LNR2pem0BS1BAtMFuOR_e-Mdl4'
        sheet_name = 'данные'

        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.worksheet(sheet_name)
        data = worksheet.get_all_records()

        df = pd.DataFrame(data)
        required_columns = ['Номер менеджера', 'ФИО', 'ID']
        df.columns = df.columns.str.strip()

        if all(column in df.columns for column in required_columns):
            new_df = df[required_columns]

            for index, row in new_df.iterrows():
                manager_id = row['ID']
                manager_type = row['Номер менеджера'].strip()

                if pd.isnull(manager_id) or pd.isnull(manager_type) or not manager_type:
                    logger.warning(f"Пропущенные данные в строке {index + 1}: {row.to_dict()}")
                    continue

                if re.match(r'Менеджер \d+', manager_type):
                    managers['CLO_MANAGER'].append(manager_id)
                elif 'Старший менеджер' in manager_type:
                    managers['SENIOR_CLO_MANAGER'].append(manager_id)
                elif 'Сопровождение' in manager_type:
                    managers['ACCOUNT_MANAGER'].append(manager_id)
                elif 'Исполнительный директор' in manager_type:
                    managers['EXECUTIVE_DIRECTOR'].append(manager_id)
                else:
                    logger.warning(f"Неизвестный тип менеджера в строке {index + 1}: {row.to_dict()}")

            return managers

        else:
            logger.error("В загруженных данных отсутствуют необходимые колонки!")
            return None

    except Exception as e:
        logger.error(f"Произошла ошибка при загрузке или обработке данных: {e}")
        return None

# просто попробовал вставить данные - все супер
# def add_row_to_spreadsheet(new_row):
#     try:
#         spreadsheet_id = '1jY-6h7R05p6BG617_LNR2pem0BS1BAtMFuOR_e-Mdl4'
#         sheet_name = 'данные'

#         spreadsheet = client.open_by_key(spreadsheet_id)
#         worksheet = spreadsheet.worksheet(sheet_name)

#         data = worksheet.get_all_records()
#         df = pd.DataFrame(data)

#         if len(df) >= 18:
#             df.loc[17] = new_row
#             worksheet.update([df.columns.values.tolist()] + df.values.tolist())
#             print("Новая запись успешно добавлена в 18-ю строку.")
#         else:
#             logger.warning("Недостаточно строк для добавления записи в 18-ю строку.")

#     except Exception as e:
#         logger.error(f"Произошла ошибка при добавлении записи: {e}")

# new_record = ['Менеджер 1', 'Иванов Иван Иванович', '12345']
# add_row_to_spreadsheet(new_record)
