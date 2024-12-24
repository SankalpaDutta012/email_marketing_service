  # config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
     SECRET_KEY = os.environ.get("SECRET_KEY") or "your_secret_key"
     SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
     SENDGRID_FROM_ADDRESS = os.environ.get("SENDGRID_FROM_ADDRESS")
     DATABASE_URL = os.environ.get("DATABASE_URL") or 'sqlite:///app.db'
     print(f'DATABASE_URL is {DATABASE_URL}')