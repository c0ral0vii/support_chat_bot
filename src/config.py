from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

BOT_TOKEN=str(os.environ.get("BOT_TOKEN"))
DB_HOST=str(os.environ.get("DB_HOST"))
DB_NAME=str(os.environ.get("DB_NAME"))
DB_PASS=str(os.environ.get("DB_PASS"))
DB_PORT=str(os.environ.get("DB_PORT"))
DB_USER=str(os.environ.get("DB_USER"))
ADMINS_LIST = os.environ.get("ADMINS_LIST", "")
ADMINS_LIST = list(map(int, ADMINS_LIST.split(","))) if ADMINS_LIST else []