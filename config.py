import os
import redis
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
import re
import pytz

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
OFFSET = os.getenv('OFFSET')
FIRST_DAY = os.getenv('FIRST_DAY')
LAST_DAY = os.getenv('LAST_DAY')

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
        offset = timezone(timedelta(seconds=TIMEZONE))

        data = {
            'bot_date': date,
            'last_updated': datetime.now(offset).strftime('%Y-%m-%d'),
        }

        with open("bot_date.txt", "w") as file:
            for key, value in data.items():
                file.write(f"{key}={value}\n")

        cls.bot_date = cls.read_date() #updates our variables to match the txt file we just wrote

    #returns a unix date as that's what we use
    #difference is in seconds
    def localize_to_location(date, time_dif):
        local_tz = pytz.timezone(TIMEZONE)
        naive_date = datetime.fromisoformat(date)
        date = local_tz.localize(naive_date) + timedelta(seconds=time_dif)
        return date.timestamp()
    
    @classmethod
    def rollover_date(cls):
        bot_date = cls.read_date() #making sure we're updated to the latest txt file
        next_day = cls.localize_to_location(bot_date, 86400)  #adds one day to our date
        if next_day >= LAST_DAY: #can't go beyond our last day in our data
            unix_date = datetime.strptime(bot_date, '%Y-%m-%d').timestamp()
            date = (unix_date - LAST_DAY) + FIRST_DAY #lands us at our time difference from the first day in the data
            date = datetime.fromtimestamp(date).replace(tzinfo=timezone(timedelta(seconds=TIMEZONE)))
        else:
            restart_event = cls.rolling_out_of_event(next_day.strftime('%Y-%m-%d')) #can either return None or the unix timestamp of the event start
            if restart_event != None: #checking to make sure we're not rolling out of the current event prematurely (ie, before a mod ends it)
                date = datetime.fromtimestamp(restart_event)
            else:
                date = next_day
        cls.write_date(date.strftime('%Y-%m-%d'))
        return cls.read_date()

    def add_event(self, new_event):
        for event in self.all_events:
            if event.event_redis_key == new_event.event_redis_key and event.start_unix == new_event.start_unix and event.end_unix == new_event.end_unix:
                print(self.all_events)
                return
            elif event.event_redis_key == new_event.event_redis_key:
                event = new_event
        self.all_events.append(new_event)
        print(self.all_events)
    
    def remove_event(self, redis_path):
        if len(self.all_events) > 0:
            for event in self.all_events:
                if event.event_redis_key == redis_path:
                    self.all_events.remove(event)
                    return 'Removed event from bot memory.'
        else:
            return 'No such event found in bot memory.'

    def get_events(self):
        s = ""
        for event in self.all_events:
            s += str(event) + '\n'
        return s
    
    @classmethod
    def check_if_event(cls, date):
        #and we're avoiding using the utils to prevent a circular import. cry cry
        unix_date = cls.localize_to_location(date, OFFSET) #360 seconds
        if (len(cls.all_events) > 0):
            for event in cls.all_events:
                if unix_date >= event.start_unix and unix_date <= event.end_unix:
                    print(f"event found; redis key {event.event_redis_key}")
                    return event.event_redis_key
        return None
    
    @classmethod
    def rolling_out_of_event(cls, new_date): #should return a unix date - if we're rolling out of an event, return the date of the first day of the event
        bot_date_key = cls.check_if_event(cls.bot_date)
        new_date_key = cls.check_if_event(new_date)
        if bot_date_key != None and new_date_key == None:
            for event in cls.all_events:
                if event.event_redis_key == bot_date_key:
                    return event.start_unix
        else:
            return None


        

    
    
