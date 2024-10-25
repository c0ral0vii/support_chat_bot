import pandas as pd
from src.logger import logger

try:
    df = pd.read_csv('https://docs.google.com/spreadsheets/d/1jY-6h7R05p6BG617_LNR2pem0BS1BAtMFuOR_e-Mdl4/gid=995008266&output=csv')
    required_columns = ['номер менеджера', 'ФИО', 'ID']
    df.columns = df.columns.str.strip()

    print(df.columns)

    if all(column in df.columns for column in required_columns):
        new_df = df[required_columns]

        for index, row in new_df.iterrows():
            if pd.isnull(row['номер менеджера']) or pd.isnull(row['ФИО']) or pd.isnull(row['ID']):
                logger.warning(f"Пропущенные данные в строке {index + 1}: {row.to_dict()}")
            else:
                logger.info(f"Данные менеджера: {row.to_dict()}")

        print(new_df.head())
    else:
        logger.error("В загруженных данных отсутствуют необходимые колонки!")

except Exception as e:
    logger.error(f"Произошла ошибка при загрузке или обработке данных: {e}")
