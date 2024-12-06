import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.services.database.models import UserCategory
from src.services.config.config import settings

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = settings.get_manager_link

async def get_managers():
    credentials = None

    if os.path.exists("input_api/token.json"):
        credentials = Credentials.from_authorized_user_file("./input_api/token.json", SCOPES)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("input_api/credentials.json", SCOPES)
            credentials = flow.run_local_server(port=0)
        with open("input_api/token.json", "w") as token:
            token.write(credentials.to_json())

    try:
        service = build("sheets", "v4", credentials=credentials)
        sheets = service.spreadsheets()

        result = sheets.values().get(spreadsheetId=SPREADSHEET_ID, range="данные!A1:C17").execute()

        values = result.get("values", [])

        managers = {}
        for row in values:
            status = row[0].split()
            if status[0] == 'Менеджер':
                status = UserCategory.CLO_MANAGER
            if status[0] == 'Сопровождение':
                status = UserCategory.ACCOUNT_MANAGER
            if status[0] == 'Старший':
                status = UserCategory.SENIOR_CLO_MANAGER
            if status[0] == 'Исполнительный':
                status = UserCategory.EXECUTIVE_DIRECTOR

            name = row[1].split()
            user_id = row[-1]
            if row[0].split()[0].lower() == "менеджер":
                field = row[0].lower()
            else:
                field = row[0]

            if len(row[-1]) > 2:
                managers[user_id] = {"status": status, "name": name, "field": field}
        return managers
    except HttpError as error:
        print(error)