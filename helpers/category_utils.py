from datetime import datetime
from config import SharedState
import pytz
from datetime import datetime, timedelta


def get_unix_date(date):
    #our data happens at 1am, 9am, etc, so...
    naive_date = datetime.strptime(date, '%Y-%m-%d') + timedelta(minutes=60)
    #we're in PST, ergo
    tz = pytz.timezone('US/Pacific')
    aware_date = tz.localize(naive_date)
    #unix timestamp as int so it can be compared
    return int(aware_date.timestamp())

def get_day_or_night():
    tz = pytz.timezone('US/Pacific')
    stringified = str(datetime.now(tz)).split(' ')[1][:2] #will get us the hours of a current day in 24hr format
    hours = int(stringified)
    if hours > 18 or hours < 6:
        return "n" #night is from 6pm to 6am (could do this by sunset/sunrise but not worth the bloat of more api checks)
    else:
        return "d"
    
def categorize_temperature(averages):
    temp = int(averages['temp'])
    if temp <= 32:
        return "arctic"
    elif temp > 32 and temp <= 49:
        return "cold"
    elif temp >= 50 and temp <= 75:
        return "mild"
    else:
        return "hot"

def categorize_weather(data):
    allWeather = []
    for entry in data:
        weather = entry['weather'][0]['main']
        allWeather.append(weather)
        
    #most common weather condition over this time period
    top_weather = sorted(allWeather, key = allWeather.count, reverse = True)[0]

    #grabbing a matching description - we don't care about 1:1 matching the IRL conditions on this date
    #just plausible realism
    for entry in data:
        if entry['weather'][0]['main'] == top_weather:
           description = entry['weather'][0]['description']
           icon = entry['weather'][0]['icon'] #gives us the png name for the openweatherapi
           return top_weather, description, icon
        
    return top_weather, None


#doing it by meteorlogical instead of astronomic seasons
#ergo each season starts on the 1st of a month 
def categorize_season():
    yyyymmdd = SharedState.bot_date.split("-")
    m = int(yyyymmdd[1])
    if m >= 3 and m <= 5:
        return "spring"
    elif m >= 6 and m <= 8:
        return "summer"
    elif m >= 9 and m <= 11:
        return "autumn"
    else:
        return "winter"
    
def calculate_uptime():
        current_time = datetime.now()
        uptime = current_time - SharedState.start_time

        #formatting our beautiful dayshoursminutesseconds etc
        days, seconds = uptime.days, uptime.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        return days, hours, minutes, seconds