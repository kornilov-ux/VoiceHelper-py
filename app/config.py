import os
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
UPLOAD_DIRECTORY = os.getenv("UPLOAD_DIRECTORY")
VOSK_MODEL_PATH = os.getenv("VOSK_MODEL")
AUTH_KEY_VALUE = os.getenv("AUTH_KEY")

