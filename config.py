import os
import redis
from dotenv import load_dotenv
from helpers.event import Event
from datetime import datetime, timezone, timedelta
import re
import pytz
from typing import Dict

load_dotenv()

#discord tokennn
TOKEN = os.getenv('DISCORD_TOKEN')
#Discord guild
GUILD = os.getenv('GUILD')

#redis stuff
PORT = int(os.getenv('PORT'))
PASSWORD = os.getenv('PASSWORD')
USERNAME = os.getenv('USERNAME')
BASE_URL = os.getenv('BASE_URL')

#general bot info.. new portsmouth, date, etc
#the stuff that's not necessarily sensitive
#but is good to be able to modify quickly for customization
LOCATION = os.getenv('LOCATION')
TIMEZONE = os.getenv('PYTZ_TIMEZONE')
ADMIN_ROLE = os.getenv('ROLE')
OFFSET = int(os.getenv('OFFSET'))
FIRST_DAY = int(os.getenv('FIRST_DAY'))
LAST_DAY = int(os.getenv('LAST_DAY'))

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
    all_events: Dict[str, Event] = { } #every key should be a redis key that matches to an Event object of {key=str; unix_start=int; unix_end=int} structure

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
        tz = pytz.timezone(TIMEZONE)
        data = {
            'bot_date': date,
            'last_updated': datetime.now(tz).strftime('%Y-%m-%d'),
        }

        with open("bot_date.txt", "w") as file:
            for key, value in data.items():
                file.write(f"{key}={value}\n")

        cls.bot_date = cls.read_date() #updates our variables to match the txt file we just wrote

    #returns a unix date as that's what we use
    #difference is in seconds
    def localize_to_location(date, time_dif):
        local_tz = pytz.timezone(TIMEZONE)
        naive_date = datetime.fromisoformat(date) + timedelta(seconds=time_dif)
        localized_date = local_tz.localize(naive_date)
        return int(localized_date.timestamp())
    
    @classmethod
    def rollover_date(cls):
        bot_date = cls.read_date() #making sure we're updated to the latest txt file
        next_day = cls.localize_to_location(bot_date, 86400)  #adds one day to our date
        if next_day >= LAST_DAY: #can't go beyond our last day in our data
            unix_date = int(datetime.strptime(bot_date, '%Y-%m-%d').timestamp())
            date = (unix_date - LAST_DAY) + FIRST_DAY #lands us at our time difference from the first day in the data
            date = cls.localize_to_location(date, -28800) #returns unix time
        else:
            restart_event = cls.rolling_out_of_event(datetime.fromtimestamp(next_day).strftime('%Y-%m-%d')) #can either return None or the unix timestamp of the event start
            if restart_event != None: #checking to make sure we're not rolling out of the current event prematurely (ie, before a mod ends it)
                date = restart_event
            else:
                date = next_day
        cls.write_date(datetime.fromtimestamp(date).strftime('%Y-%m-%d'))
        return cls.read_date()

    @classmethod
    def add_event(cls, new_event: Event):
        all_events = cls.all_events
        if all_events: #if it's not empty
            for redis_key in all_events.keys():
                event = all_events[redis_key]
                if event.is_same_event(new_event): return #if they're the same, don't do anything
                elif event.get_key() == new_event.get_key():
                    all_events[redis_key] = new_event #elsewise replace the old event, just like what would happen in redis
                    return
        new_key = new_event.get_key()
        all_events[new_key] = new_event
    
    @classmethod
    def remove_event(cls, redis_path):
        return cls.all_events.pop(redis_path, None)
    
    @classmethod
    def get_current_event(cls):
        bot_date = cls.bot_date
        return cls.check_if_event(bot_date)

    
    @classmethod
    def end_current_event(cls):
        bot_date = cls.bot_date
        event_key = cls.check_if_event(bot_date)
        if event_key != None:
            cls.remove_event(event_key)
        return event_key


    def get_events(self):
        s = ""
        for event in self.all_events.values():
            s += str(event) + '\n'
        return s
    
    @classmethod
    def get_event(cls, redis_key):
        all_events = cls.all_events
        return all_events[redis_key] if redis_key in all_events else None
    
    @classmethod
    def check_if_event(cls, date):
        #and we're avoiding using the utils to prevent a circular import. cry cry
        unix_date = cls.localize_to_location(date, OFFSET) #3600 seconds
        all_events = cls.all_events
        if all_events:
            for event in all_events.values():
                if unix_date >= event.get_start() and unix_date <= event.get_end():
                    return event.get_key()
        return None
    
    @classmethod
    def rolling_out_of_event(cls, new_date): #should return a unix date - if we're rolling out of an event, return the date of the first day of the event
        bot_date_key = cls.check_if_event(cls.bot_date)
        new_date_key = cls.check_if_event(new_date)
        if bot_date_key != None and new_date_key == None:
            for event_key in cls.all_events.keys():
                if event_key == bot_date_key:
                    return cls.all_events[event_key].start_unix
        else:
            return None


        

    
    
