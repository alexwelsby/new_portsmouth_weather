# bot.py
import os
import random
import requests
from dotenv import load_dotenv
from dateutil.parser import parse
from datetime import datetime, timedelta
from dateutil.tz.tz import tzoffset
from collections import defaultdict
from report_template import weather_data, weather_report

import discord
from discord.ext import commands

import redis
import json

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
PORT = int(os.getenv('PORT'))
PASSWORD = os.getenv('PASSWORD')
USERNAME = os.getenv('USERNAME')
BASE_URL = os.getenv('BASE_URL')
LOCATION = os.getenv('LOCATION')

#redis database connection
redis_client = redis.StrictRedis(
    host=BASE_URL,
    port=PORT,
    username=USERNAME,
    password=PASSWORD,
    decode_responses=True
)

start_time = 0
uptime = 0

bot_date = '2023-02-01'

ALL_MODES = ["auto", "manual"]
current_mode = ALL_MODES[0] #will be auto


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    global start_time
    start_time = datetime.now()
    calculateUptime()
    print(f'Bot\'s start time has been set to {start_time}. Current uptime: {uptime} (Uptime is used to decide when to advance the calendar in Auto mode.)')


#parent group for weatherbot commands
@bot.group(invoke_without_command=True)
async def weather(ctx):
    await ctx.send("Available subcommands: report, setdate, getdate. Use '!weather <subcommand>'.")

def get_unix_date():
    yyyymmdd = bot_date.split("-")
    y = int(yyyymmdd[0])
    m = int(yyyymmdd[1])
    d = int(yyyymmdd[2])
    #we should assume we're in PST, ergo -28800
    return int(datetime(y, m, d, tzinfo=tzoffset(None, -28800)).timestamp())


@weather.command(name='report', help='Gets current weather for New Portsmouth.')
async def report(ctx):
    try:
        result = get_current_json()
        if result != "":
            message = build_weatherman(result)
            await ctx.send(message)
        else:
            await ctx.send(f"No event found for {bot_date}.")
    except Exception as e:
        await ctx.send(f"Error blowing up data: {e}")

def build_weatherman(result):
    averages = calculate_averages(result)
    weather_type, weather_description = categorize_weather(result)
    season = categorize_season() #checks from global bot_date so needs nothing passed
    print(f"Season has been categorized as {season}.")
    temp_type = categorize_temperature(averages)

    data = {
        'location': LOCATION,
        'time_period': "day",
        'weather_description': weather_description, 
        'temp_min': averages['temp_min'],
        'temp_max': averages['temp_max'],
        'temp': averages['temp'],
        #'precipitation': averages['precipitation'], haven't added precipitations to json yet
        'precipitation': 0.25,
        'season': season,
        'temp_type': temp_type,
        'weather': weather_type,
    }

    print(f"Final data structure is {data}.")

    weather_dat = weather_data(data)
    weatherman = weather_report()
    return (weatherman.generate_report(weather_dat))

def build_info(data):
    pass

def categorize_temperature(averages):
    temp = int(averages['temp'])
    if temp <= 32:
        return "arctic"
    elif temp > 32 & temp <= 49:
        return "cold"
    elif temp >= 50 & temp <= 75:
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
           return top_weather, description
        
    return top_weather, None


#doing it by meteorlogical instead of astronomic seasons
#ergo each season starts on the 1st of a month 
def categorize_season():
    yyyymmdd = bot_date.split("-")
    m = int(yyyymmdd[1])
    if m >= 3 and m <= 5:
        return "spring"
    elif m >= 6 and m <= 8:
        return "summer"
    elif m >= 9 and m <= 11:
        return "autumn"
    else:
        return "winter"

def calculate_averages(data):
    totals = {
        'temp': 0, 'temp_min': 0, 'temp_max': 0, 'feels_like': 0,
        'pressure': 0, 'humidity': 0, 'dew_point': 0,
        'clouds_all': 0, 'wind_speed': 0, 'wind_deg': 0, 'wind_gust': 0
    }
    count = 0

    for entry in data:
        count += 1
        main = entry['main']
        totals['temp'] += main['temp']
        totals['temp_min'] += main['temp_min']
        totals['temp_max'] += main['temp_max']
        totals['feels_like'] += main['feels_like']
        totals['pressure'] += main['pressure']
        totals['humidity'] += main['humidity']
        totals['dew_point'] += main['dew_point']
        totals['clouds_all'] += entry['clouds']['all']
        wind = entry['wind']
        totals['wind_speed'] += wind['speed']
        totals['wind_deg'] += wind['deg']
        if wind['gust'] != '':  #catching when wind_gust is blank
            totals['wind_gust'] += float(wind['gust'])
        #TODO: collapse rain1hr/2hr/3hr and snow1hr/2hr/3hr into one column 'Precipitation' in csv_to_json

    averages = {key: round(value / count, 1) for key, value in totals.items()}
    print(f"Averages have been categorized as {averages}.")
    return averages



def get_current_json():
    curMonth = bot_date[:-3] #chops it to yyyy-mm (what the json keys are)
    result = ""
    if redis_client.exists(curMonth):  #check if the key exists
        json_data = redis_client.execute_command('JSON.GET', curMonth)
        data = json.loads(json_data) #loads it into a list
        result = [item for item in data if bot_date in item.get('dt_iso')] #fetches every hourly report on this date
    return result


@weather.command(name='setdate', help='Set the current date of the weather bot. (In auto mode, it will begin counting up from this date.)')
async def setDate(ctx, *, date:str):
    global bot_date
    dt = parse(date)
    bot_date = dt.strftime('%Y-%m-%d')
    response = "My current date is " + bot_date + "."
    await ctx.send(response)

@weather.command(name='getdate', help='Get the current date of the weather bot.')
async def getDate(ctx):
    response = "My current date is " + bot_date + "."
    await ctx.send(response)

@weather.command(name='uptime')
async def getUptime(ctx):
    days, hours, minutes, seconds = calculateUptime()
    """if days % 7 == 0 & current_mode == "auto":
        #if the bot is set to auto it advances the days itself, ergo:
        advanceWeek()
        change this so it happens automatically?!"""
    formatted_uptime = f"Uptime: {days}d {hours}h {minutes}m {seconds}s"
    await ctx.send(formatted_uptime)

def createEmbed(json, city_name, ctx):
    overview = json["overview"]
    embed = discord.Embed(title=f"Weather in {city_name}",
        color=ctx.guild.me.top_role.color,
        timestamp=ctx.message.created_at,)
    embed.add_field(name="Today's weather", value=f"**{overview}**", inline=False)
    embed.set_thumbnail(url="https://i.ibb.co/CMrsxdX/weather.png")
    embed.set_footer(text=f"Requested by {ctx.author.name}")
    return embed


def calculateUptime():
    global uptime
    current_time = datetime.now()
    uptime = current_time - start_time 

    #formatting our beautiful dayshoursminutesseconds etc
    days, seconds = uptime.days, uptime.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    return days, hours, minutes, seconds



bot.run(TOKEN)