# bot.py
import os
import random
import requests
from dotenv import load_dotenv
from dateutil.parser import parse
from datetime import datetime, timedelta

import discord
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
API_KEY = os.getenv('API_KEY')
BASE_URL = os.getenv('BASE_URL')

ALL_MODES = ['auto', 'manual']

start_time = 0
uptime = 0

bot_date = '2023/02/01'


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

"""These are all just here for my reference 

@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my Discord server!'
    )

@bot.command(name='99')
async def nine_nine(ctx):
    brooklyn_99_quotes = [
        'I\'m the human form of the 💯 emoji.',
        'Bingpot!',
        (
            'Cool. Cool cool cool cool cool cool cool, '
            'no doubt no doubt no doubt no doubt.'
        ),
    ]

    response = random.choice(brooklyn_99_quotes)
    await ctx.send(response)
    
@bot.command(name='roll_dice', help='Simulates rolling dice.')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    try:
        # Validate input: Ensure numbers are positive
        if number_of_dice <= 0 or number_of_sides <= 0:
            await ctx.send("Both the number of dice and the number of sides must be positive integers.")
            return
        
        # Generate dice rolls
        dice = [
            str(random.choice(range(1, number_of_sides + 1)))
            for _ in range(number_of_dice)
        ]
        await ctx.send(', '.join(dice))
    except ValueError:
        await ctx.send("Invalid parameters. Usage: !roll_dice <number_of_dice> <number_of_sides>")

@roll.error
async def roll_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing arguments. Usage: !roll_dice <number_of_dice> <number_of_sides>")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Invalid argument type. Please ensure both inputs are integers. Usage: !roll_dice <number_of_dice> <number_of_sides>")
 
End of reference methods
 """
#parent group for weatherbot commands
@bot.group(invoke_without_command=True)
async def weather(ctx):
    await ctx.send("Available subcommands: report, setdate, getdate. Use '!weather <subcommand>'.")

@weather.command(name='report', help='Gets current weather for New Portsmouth.')
async def report(ctx):
    fictional_city = 'New Portsmouth'
    real_city = 'Sequim'
    complete_url = BASE_URL + "appid=" + API_KEY + "&q=" + real_city + "&units=imperial"
    response = requests.get(complete_url)
    json = response.json()
    
    channel = ctx.message.channel
    if json["cod"] != "404":
        async with channel.typing():
            embed = createEmbed(json, fictional_city, ctx)
            await channel.send(embed=embed)
    else:
        await channel.send("City not found.")

@weather.command(name='setdate', help='Set the current date of the weather bot. (It will begin counting up from this date.)')
async def setDate(ctx, *, date:str):
    global bot_date
    dt = parse(date)
    bot_date = dt.strftime('%Y/%m/%d')

@weather.command(name='getdate', help='Get the current date of the weather bot.')
async def getDate(ctx):
    response = "My current date is " + bot_date
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


#modified from https://stackoverflow.com/questions/63486570/how-to-make-a-weather-command-using-discord-py-v1-4-1
"""def createEmbed(json, city_name, ctx):
    print("ctx", ctx)
    main = json["main"]
    current_temperature = main["temp"]
    current_pressure = main["pressure"]
    current_humidity = main["humidity"]
    weather = json["weather"]
    weather_description = weather[0]["description"]
    embed = discord.Embed(title=f"Weather in {city_name}",
        color=ctx.guild.me.top_role.color,
        timestamp=ctx.message.created_at,)
    embed.add_field(name="Description", value=f"**{weather_description}**", inline=False)
    embed.add_field(name="Temperature(F)", value=f"**{current_temperature}°F**", inline=False)
    embed.add_field(name="Humidity(%)", value=f"**{current_humidity}%**", inline=False)
    embed.add_field(name="Atmospheric Pressure(hPa)", value=f"**{current_pressure}hPa**", inline=False)
    embed.set_thumbnail(url="https://i.ibb.co/CMrsxdX/weather.png")
    print(json)
    embed.set_footer(text=f"Requested by {ctx.author.name}")
    return embed"""

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
