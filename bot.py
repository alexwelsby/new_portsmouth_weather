# bot.py
import discord
import asyncio
from discord.ext import commands
from config import TOKEN, SharedState
from helpers.category_utils import calculate_uptime
from helpers.redis_utils import populate_events_vars

start_time = 0
uptime = 0
auto_advance = True

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    days, hours, minutes, seconds = calculate_uptime()
    bot_date = SharedState.read_date()
    populate_events_vars()
    print(f'Bot\'s current date is {bot_date}. Current uptime: {days} days, {hours} hours, {minutes} minutes, and {seconds} seconds (Uptime is used to decide when to advance the calendar in Auto mode.)')
    bot.loop.create_task(check_for_rollover(days)) #if auto_advance is true, advances the current date by 1

async def check_for_rollover(days):
    while auto_advance:
        new_days, hours, minutes, seconds = calculate_uptime()
        if days != new_days:
            date = SharedState.rollover_date()
            print(f"Date has been updated to {date}")
            days = new_days
        await asyncio.sleep(300) #wait for 5 minutes before checking again

#parent group for weatherbot commands
@bot.group(invoke_without_command=True)
async def weather(ctx):
    await ctx.send("Available subcommands: report <day|week>, set_date <date>, get_date. Use '!weather <subcommand> <optional:args>'.")

async def load_extensions():
    extensions = [
        'cogs.weather',
        'cogs.date_management',
        'cogs.uptime',
        'cogs.events'
    ]
    for ext in extensions:
        await bot.load_extension(ext)

async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())