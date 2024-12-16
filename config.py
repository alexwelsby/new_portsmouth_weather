import os
import redis
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

#discord tokennn
TOKEN = os.getenv('DISCORD_TOKEN')

#redis stuff
PORT = int(os.getenv('PORT'))
PASSWORD = os.getenv('PASSWORD')
USERNAME = os.getenv('USERNAME')
BASE_URL = os.getenv('BASE_URL')

#general bot info.. new portsmouth, date, etc
LOCATION = os.getenv('LOCATION')

redis_client = redis.StrictRedis(
    host=BASE_URL,
    port=PORT,
    username=USERNAME,
    password=PASSWORD,
    decode_responses=True
)

class SharedState:
    bot_date = os.getenv('BOT_DATE', '2023-02-01') #our fallback if there is no bot_date found
    time_period = 'week'
    start_time = datetime.now()