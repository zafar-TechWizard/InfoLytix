import os
import secrets
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=int(30))
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/InfoLytix")

