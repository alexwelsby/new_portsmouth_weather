import os
import redis
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from dateutil.parser import parse
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
    all_events = [ ] #first should be unix date of the start of the event, last is unix date of end of event
    #should add error handling later...

    @classmethod
    def read_date(cls):
        date = ""
        with open('bot_date.txt', 'r') as file:
            lines = file.readlines()
            data = dict(line.strip().split('=') for line in lines) #the label will become the key for the dict
            date = data['bot_date']
        valid = re.search(r"^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$", date)
        if (valid):
            cls.bot_date = date
        else:
            print("Error in read_date: bot_date.json does not appear to have a valid date of structure YYYY-MM-DD. Has it been modified? Fallback date set to 2023-02-01.")
            cls.bot_date = '2023-02-01' #our fallback
        return cls.bot_date

    @classmethod
    def write_date(cls, date):
        offset = timezone(timedelta(seconds=-28800))

        data = {
            'bot_date': date,
            'last_updated': datetime.now(offset).strftime('%Y-%m-%d'),
        }

        with open("bot_date.txt", "w") as file:
            for key, value in data.items():
                file.write(f"{key}={value}\n")

        cls.bot_date = cls.read_date() #updates our variables to match the txt file we just wrote
    
    @classmethod
    def rollover_date(cls):
        offset = timezone(timedelta(seconds=-28800))
        bot_date = cls.read_date()
        next_day = (datetime.fromisoformat(bot_date) + timedelta(days=1)).replace(tzinfo=timezone(timedelta(seconds=-28800)))  #adds one day to our date
        if next_day.timestamp() >= 1733587200.0: #can't go beyond our last day in our data
            unix_date = datetime.strptime(bot_date, '%Y-%m-%d').timestamp()
            date = (unix_date - 1733587200) + 1672531200 #lands us at our time difference from the first day in the data
            date = datetime.fromtimestamp(date).replace(tzinfo=timezone(timedelta(seconds=-28800)))
        else:
            date = next_day
        cls.write_date(date.strftime('%Y-%m-%d'))
        return cls.read_date()

    def add_event(self, new_event):
        for event in self.all_events:
            if event.event_redis_key == new_event.event_redis_key and event.start_unix == new_event.start_unix and event.rnd_unix == new_event.end_unix:
                print(self.all_events)
                return
        self.all_events.append(new_event)
        print(self.all_events)
    
    def end_event(self, redis_path):
        for event in self.all_events:
            if event.event_redis_key == redis_path:
                self.all_events.remove(event)

    def get_events(self):
        s = ""
        for event in self.all_events:
            s += str(event) + '\n'
        return s

    
    
