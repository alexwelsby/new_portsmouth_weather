import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
PORT = int(os.getenv("PORT"))
PASSWORD = os.getenv("PASSWORD")
USERNAME = os.getenv("USERNAME")
BASE_URL = os.getenv("BASE_URL")
LOCATION = os.getenv("LOCATION")