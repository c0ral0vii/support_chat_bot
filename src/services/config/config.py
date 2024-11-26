from dotenv import load_dotenv, find_dotenv
import os


class Settings:
    def __init__(self):
        load_dotenv(find_dotenv())

        self._BOT_TOKEN = str(os.environ.get("BOT_TOKEN"))

        if not self._BOT_TOKEN:
            assert 'Not set bot token'

        # db

        self.DB_HOST = str(os.environ.get("DB_HOST")) # '0.0.0.0'
        self.DB_NAME = str(os.environ.get("DB_NAME"))
        self.DB_PASS = str(os.environ.get("DB_PASS"))
        self.DB_PORT = str(os.environ.get("DB_PORT"))
        self.DB_USER = str(os.environ.get("DB_USER"))

        # default link for managers

        self._MANAGERS_LINK = "1jY-6h7R05p6BG617_LNR2pem0BS1BAtMFuOR_e-Mdl4"

        # debug

        self._DEBUG = os.environ.get("DEBUG", False)


    @property
    def get_debug_settings(self):
        return self._DEBUG

    @property
    def get_database_link(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def get_bot_token(self):
        return self._BOT_TOKEN

    @property
    def get_manager_link(self):
        return self._MANAGERS_LINK


settings = Settings()