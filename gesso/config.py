import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'gesso.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    OAUTH_CLIENT_ID = os.environ.get("OAUTH_CLIENT_ID", "")
    OAUTH_CLIENT_SECRET = os.environ.get("OAUTH_CLIENT_SECRET", "")

    WTF_CSRF_ENABLED = True