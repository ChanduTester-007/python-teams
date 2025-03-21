import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TEAMS_APP_ID = os.getenv("TEAMS_APP_ID")
    TEAMS_APP_PASSWORD = os.getenv("TEAMS_APP_PASSWORD")
