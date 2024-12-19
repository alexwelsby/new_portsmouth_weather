import json
import discord
from helpers.report_template import weather_data, weather_report
from helpers.category_utils import get_day_or_night, categorize_season, categorize_weather, categorize_temperature
from config import LOCATION, SharedState

def build_weatherman(result):
    averages = calculate_averages(result)
    weather_type, weather_description, weather_icon = categorize_weather(result)
    season = categorize_season() #checks from global bot_date so needs nothing passed
    print(f"Season has been categorized as {season}.")
    temp_type = categorize_temperature(averages)
    data = {
        'location': LOCATION,
        'time_period': SharedState.time_period,
        'weather_description': weather_description, 
        'temp_min': averages['temp_min'],
        'temp_max': averages['temp_max'],
        'temp': averages['temp'],
        'humidity': averages['humidity'],
        'precipitation': averages['precipitation'], 
        'season': season,
        'temp_type': temp_type,
        'weather': weather_type,
        'weather_icon': weather_icon,
    }

    print(f"Final data structure is {data}.")

    weather_dat = weather_data(data)
    weatherman = weather_report()
    return data, weatherman.generate_report(weather_dat)

def create_embed(data, weatherman_report, ctx):
    weather_icon = data['weather_icon'][:-1] + get_day_or_night() #chops off the day/night indicator (we're going to match it to current day/night in the PNW)

    embed = discord.Embed(title=f"This {data['time_period']}'s weather in {data['location']}",
        color=ctx.guild.me.top_role.color,
        timestamp=ctx.message.created_at,)
    embed.set_author(name="New Portsmouth Weather", icon_url=f"https://openweathermap.org/img/wn/{weather_icon}.png")
    embed.add_field(name="Description", value=f"**{weatherman_report}**", inline=False)
    embed.add_field(name="Temperature(F)", value=f"**{data["temp"]}°F**", inline=True)
    embed.add_field(name="Humidity(%)", value=f"**{data['humidity']}%**", inline=True)
    embed.add_field(name="Average high (F)", value=f"**{data["temp_max"]}°F**", inline=True)
    embed.add_field(name="Average low (F)", value=f"**{data["temp_min"]}°F**", inline=True)
    embed.set_thumbnail(url=f"https://openweathermap.org/img/wn/{weather_icon}.png")
    embed.set_footer(text=f"Requested by {ctx.author.name}")
    return embed

def calculate_averages(data):
    totals = {
        'temp': 0, 'temp_min': 0, 'temp_max': 0, 'feels_like': 0,
        'pressure': 0, 'humidity': 0, 'dew_point': 0,
        'precipitation': 0,
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
        totals['precipitation'] += entry['precipitation'] #custom precipitation field.. keep an eye on this
        totals['clouds_all'] += entry['clouds']['all']
        wind = entry['wind']
        totals['wind_speed'] += wind['speed']
        totals['wind_deg'] += wind['deg']
        if wind['gust'] != '':  #catching when wind_gust is blank
            totals['wind_gust'] += float(wind['gust'])

    averages = {key: round(value / count, 1) for key, value in totals.items()}
    print(f"Averages have been calculated as {averages}.")
    return averages

