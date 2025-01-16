import discord
from helpers.report_template import weather_data, weather_report
from helpers.category_utils import get_day_or_night, categorize_season, categorize_weather, categorize_temperature
from config import LOCATION, SharedState

def build_weatherman(result, time_period):
    if (time_period == "month" or time_period == "week"):
        pass
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
        'temp': averages['feels_like'],
        'humidity': averages['humidity'],
        'precipitation': averages['precipitation'], 
        'wind_speed': averages['wind_speed'],
        'dew_point': averages['dew_point'],
        'season': season,
        'temp_type': temp_type,
        'weather': weather_type,
        'weather_icon': weather_icon,
    }

    #print(f"Final data structure is {data}.")

    weather_dat = weather_data(data)
    weatherman = weather_report()
    return data, weatherman.generate_report(weather_dat).replace("this day", "today")

def create_embed(data, weatherman_report, interaction):
    weather_icon = data['weather_icon'][:-1] + get_day_or_night() #chops off the day/night indicator (we're going to match it to current day/night in the PNW)
    title = f"This {data['time_period']}'s weather in {data['location']}".replace("This day", "Today")
    embed = discord.Embed(title=title,
        color=interaction.guild.me.top_role.color,
        timestamp=discord.utils.utcnow(),)
    embed.set_author(name=f"{data['location']} Weather", icon_url=f"https://openweathermap.org/img/wn/{weather_icon}.png")
    embed.add_field(name="\u200b", value=f"{weatherman_report}", inline=False)
    embed.add_field(name="Average low", value=f"{data["temp_min"]}°F", inline=True)
    embed.add_field(name="Average high", value=f"{data["temp_max"]}°F", inline=True)
    embed.add_field(name="Average RealFeel", value=f"{data["temp"]}°F", inline=True)
    embed.add_field(name="Dew point", value=f"{data['dew_point']}°F", inline=True)
    embed.add_field(name="Humidity", value=f"{data['humidity']}%", inline=True)
    embed.add_field(name="Wind speed", value=f"{data['wind_speed']} MPH", inline=True)
    embed.set_thumbnail(url=f"https://openweathermap.org/img/wn/{weather_icon}.png")
    embed.set_footer(text=f"Requested by {interaction.user.name}")
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

    averages = {key: round(value / count, 1) for key, value in totals.items() if key != 'precipitation'}
    averages['precipitation'] = round(totals['precipitation'], 1) #just because the weather reports sound more natural if they describe overall precipitation...
    #does mean our variable name is inaccurate though
    #print(f"Averages have been calculated as {averages}.")
    return averages

def debug_descriptions(): #using this to proofread written descriptions for awkward verbiage/grammatical errors across all possible conditions lol
    seasons = [ "spring", "summer", "autumn", "winter"]
    temps = ["arctic", "cold", "mild", "hot"]
    conditions = ["Clear", "Clouds", "Rain", "Snow"]
    clouds_descript = ["few clouds", "scattered clouds", "broken clouds", "overcast clouds"]
    clear_descript = ["sky is clear"]
    snow_descript = ["light snow", "moderate snow", "heavy snow", "sleet", "light shower sleet", "shower sleet", "light rain and snow", "rain and snow", "light shower snow", "shower snow", "heavy shower snow"]
    rain_descript = ["light rain", "moderate rain", "heavy intensity rain", "very heavy rain", "extreme rain", "freezing rain", "light intensity shower rain", "shower rain", "heavy intensity shower rain", "ragged shower rain"]
    allOutputs = ""
    condition_descriptions = {
        "Clear": clear_descript,
        "Clouds": clouds_descript,
        "Snow": snow_descript,
        "Rain": rain_descript
    }

    for season in seasons:
        allOutputs += season + "\n"
        for temp in temps:
            allOutputs += temp + "\n"
            for condition in conditions:
                allOutputs += condition + "\n"
                for description in condition_descriptions[condition]:
                    data = {
                        'location': LOCATION,
                        'time_period': SharedState.time_period,
                        'weather_description': description, 
                        'temp_min': 65.0,
                        'temp_max': 75.0,
                        'temp': 70.0,
                        'humidity': 88.3,
                        'precipitation': 0.1, 
                        'season': season,
                        'temp_type': temp,
                        'weather': condition,
                        'weather_icon': '13d',
                    }
                    weather_dat = weather_data(data)
                    weatherman = weather_report()
                    allOutputs += weatherman.generate_report(weather_dat) + "\n"

    return allOutputs

