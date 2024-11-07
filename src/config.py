from dotenv import load_dotenv, find_dotenv
from src.utils.user_data_parser import load_managers_ids
import os

# 7757698162, 1061359692

# получаем словарь внутри которого данные из google docs
managers = load_managers_ids()
load_dotenv(find_dotenv())

BOT_TOKEN=str(os.environ.get("BOT_TOKEN"))
DB_HOST=str(os.environ.get("DB_HOST"))
DB_NAME=str(os.environ.get("DB_NAME"))
DB_PASS=str(os.environ.get("DB_PASS"))
DB_PORT=str(os.environ.get("DB_PORT"))
DB_USER=str(os.environ.get("DB_USER"))
ADMINS_LIST = os.environ.get("ADMINS_LIST", "")
ADMINS_LIST = list(map(int, ADMINS_LIST.split(","))) if ADMINS_LIST else []
CLO_MANAGER = managers['CLO_MANAGER']
SENIOR_CLO_MANAGER = managers['SENIOR_CLO_MANAGER']
ACCOUNT_MANAGER = managers['ACCOUNT_MANAGER']
EXECUTIVE_DIRECTOR = managers['EXECUTIVE_DIRECTOR']

# print("BOT_TOKEN:", BOT_TOKEN)
# print("DB_HOST:", DB_HOST)
# print("DB_NAME:", DB_NAME)
# print("DB_PASS:", DB_PASS)
# print("DB_PORT:", DB_PORT)
# print("DB_USER:", DB_USER)
# print("ADMINS_LIST:", ADMINS_LIST)
# print("CLO_MANAGER:", CLO_MANAGER)
# print("SENIOR_CLO_MANAGER:", SENIOR_CLO_MANAGER)
# print("ACCOUNT_MANAGER:", ACCOUNT_MANAGER)
# print("EXECUTIVE_DIRECTOR:", EXECUTIVE_DIRECTOR)