from config import redis_client, SharedState
from helpers.category_utils import get_unix_date
from helpers.event import Event
import redis
import ujson as json

def add_to_redis(key, data):
    try:
        redis_client.execute_command('JSON.SET', key, '.', json.dumps(data))
        print(f"{key} stored using RedisJSON.")
    except redis.exceptions.ResponseError:
        redis_client.set(key, json.dumps(data))
        print(f"{key} stored as a string.")

def remove_from_redis(key):
    try:
        redis_client.execute_command('JSON.DEL', key)
        return f"Deleted {key} from redis."
    except redis.exceptions.ResponseError:
        return f"Key not found: Did you mistype it?"
        

def populate_events_vars(): #assuming our bot went offline, we need to double-check with the redis database and re-add them to our vars
    all_keys = redis_client.keys('*')
    event_keys = [key for key in all_keys if 'EVENT' in key] #grabbing all keys w 'EVENT' in them

    for key in event_keys:
        json_data = redis_client.execute_command('JSON.GET', key)
        data = json.loads(json_data) #loads it into a list
        start_unix = data[0]['dt']
        end_unix = data[-1]['dt']
        #repeat code but i am tired. avoiding circular imports
        event = Event(event_redis_key=key, start_unix=start_unix, end_unix=end_unix)
        SharedState.add_event(SharedState, event)
        print(SharedState.get_events(SharedState))
        
def get_current_json(bot_date, event_key, time_period): 
    if event_key != None:
        key = event_key
    else:
        key = bot_date[:-3] #chops it to yyyy-mm (what the json keys are)
    result = ""
    if redis_client.exists(key):  #check if the key exists
        json_data = redis_client.execute_command('JSON.GET', key)
        data = json.loads(json_data) #loads it into a list

        start_date = get_unix_date(bot_date) #this will be the beginning of our range
        end_date = get_end_date(start_date, time_period)
        
        result = [item for item in data if start_date <= item.get('dt') <= end_date] #filters down to items with unix dates that fall between start and end
        
        if result[-1].get('dt') >= end_date: #results were all in this month; don't need to get anymore json
            return result
        else: #means our end-date falls outside of our month, ergo we must grab the next one
            next_month = get_next_month(key) #gives us a string formatted YYYY-MM of next month
            if redis_client.exists(next_month):
                json_data = redis_client.execute_command('JSON.GET', next_month)
                data = json.loads(json_data) #loads it into a list
                result.extend(item for item in data if start_date <= item.get('dt') <= end_date)
                return result

        result = [item for item in data if item.get('dt') >= start_date and item.get('dt') <= end_date] #gets all reports between start and end unix times

    return result

def get_end_date(start_date, time_period):
    multiplier = {'day': 1, 'week': 7, 'month': 30}.get(time_period, 7) #week is our fallback period
    end_date = start_date + (86400 * multiplier) #86400 is the # of seconds in a day
    return end_date

def get_next_month(curMonth):
    if "EVENT_" in curMonth:
        curMonth = curMonth[6:] #cuts event_ out
    year, month = map(int, curMonth.split('-'))
    if month == 12:  #year rollover
        return f"{year + 1}-01"
    else:
        month += 1
        if month < 10:
            return f"{year}-0{month}"
        else:
            return f"{year}-{month}"