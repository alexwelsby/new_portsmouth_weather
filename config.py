import os
import redis
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
import re

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
    time_period = 'week'
    start_time = datetime.now()
    bot_date = '2023-02-01'
    #should add error handling later...
    def read_date():
        date = Path('bot_date.txt').read_text()
        valid = re.search(r"^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$", date)
        if (valid):
            return date
        else:
            print("Error in read_date: bot_date.txt does not appear to have a valid date of structure YYYY-MM-DD. Has it been modified? Fallback date set to 2023-02-01.")
            return '2023-02-01' #our fallback
    
    bot_date = read_date()
    
    def write_date(self, date):
        file = open("bot_date.txt", "w") 
        file.write(date) 
        file.close()
        global bot_date
        bot_date = self.read_date()

    
    
