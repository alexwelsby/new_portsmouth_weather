# bot.py
import discord
import asyncio
from discord.ext import commands
import pytz
from datetime import datetime
from config import TOKEN, SharedState, GUILD, TIMEZONE
from helpers.category_utils import calculate_uptime
from helpers.redis_utils import populate_events_vars

start_time = 0
uptime = 0
auto_advance = True

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', owner_id=209034335112790022, intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    days, hours, minutes, seconds = calculate_uptime()
    bot_date = SharedState.read_date()
    populate_events_vars()
    print(f'Bot\'s current date is {bot_date}. Current uptime: {days} days, {hours} hours, {minutes} minutes, and {seconds} seconds.')
    bot.loop.create_task(check_for_rollover(days)) #if auto_advance is true, advances the current date by 1



async def check_for_rollover(days):
    seattle_tz = pytz.timezone(TIMEZONE)
    current_date = datetime.now(seattle_tz).date()
    while auto_advance:
        new_date = datetime.now(seattle_tz).date()
        if new_date != current_date:
            current_date = new_date
            date = SharedState.rollover_date()
            print(f"Date has been updated to {date}")
        await asyncio.sleep(300) #wait for 5 minutes before checking again

#parent group for weatherbot commands
@bot.group(invoke_without_command=True)
async def weather(ctx):
    await ctx.send("Available subcommands: report <day|week>, set_date <date>, get_date. Use '!weather <subcommand> <optional:args>'.")


@bot.command(name='sync', description='Owner only')
@commands.is_owner()
async def sync(ctx):
    MY_GUILD = discord.Object(id=GUILD)
    bot.tree.copy_global_to(guild=MY_GUILD)
    await bot.tree.sync(guild=MY_GUILD)
    await ctx.send('Command tree synced.')

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
        await bot.tree.sync()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())