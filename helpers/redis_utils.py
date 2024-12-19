#going to use this for mods to be able to upload custom events/weather
from config import redis_client, SharedState
from helpers.category_utils import get_unix_date
import redis
import json

def add_to_redis(name, data):
    try:
        redis_client.execute_command('JSON.SET', name, '.', json.dumps(data))
        print(f"{name} stored using RedisJSON.")
    except redis.exceptions.ResponseError:
        redis_client.set(name, json.dumps(data))
        print("{name} stored as a string.")

def get_current_json(bot_date, time_period):
    curMonth = "EVENT_" + bot_date[:-3] if SharedState.running_event else bot_date[:-3] #chops it to yyyy-mm (what the json keys are)
    result = ""
    if redis_client.exists(curMonth):  #check if the key exists
        json_data = redis_client.execute_command('JSON.GET', curMonth)
        data = json.loads(json_data) #loads it into a list

        start_date = get_unix_date(bot_date)
        multiplier = {'day': 1, 'week': 7, 'month': 30}[time_period]
        end_date = start_date + (86400 * multiplier) #86400 is the # of seconds in a day
        
        result = [item for item in data if start_date <= item.get('dt') <= end_date]

        if result[-1].get('dt') >= end_date: #results are ready to rumble
            return result
        else: #means our end-date falls outside of our month, ergo we must grab the next one
            next_month = get_next_month(curMonth) #gives us a string formatted YYYY-MM of next month
            if redis_client.exists(next_month):
                json_data = redis_client.execute_command('JSON.GET', next_month)
                data = json.loads(json_data) #loads it into a list
                result.extend(item for item in data if start_date <= item.get('dt') <= end_date)
                return result

        result = [item for item in data if item.get('dt') >= start_date and item.get('dt') <= end_date] #gets all reports between start and end unix times
    print(result)
    return result

def get_next_month(curMonth):
    year, month = map(int, curMonth.split('-'))
    if month == 12:  # Handle year rollover
        return f"{year + 1}-01"
    else:
        month += 1
        if month < 10:
            return f"{year}-0{month}"
        else:
            return f"{year}-{month}"