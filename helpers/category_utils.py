from datetime import datetime
from dateutil.tz.tz import tzoffset
from config import SharedState
import pytz

#literally so embarrassed luv i had what i felt was an elegant 5 line solution for this
#and it turns out the library just does it. itself. in one line. not sure why i didn't think of this
#well whatever. i won't remove the method. i love her too much
def get_unix_date(date):
    #we should assume we're in PST, ergo -28800
    return int(datetime.strptime(date, '%Y-%m-%d').timestamp())

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