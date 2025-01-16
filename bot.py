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
    bot.loop.create_task(check_for_rollover()) #if auto_advance is true, advances the current date by 1

async def check_for_rollover():
    tz = pytz.timezone(TIMEZONE)
    current_date = datetime.now(tz).date()
    while auto_advance:
        new_date = datetime.now(tz).date()
        if new_date != current_date:
            current_date = new_date
            date = SharedState.rollover_date()
            print(f"Date has been updated to {date}")
        await asyncio.sleep(300) #wait for 5 minutes before checking again

@bot.command(name='sync', description='Owner only')
@commands.is_owner()
async def sync(ctx):
    await bot.tree.sync()
    await ctx.send('Command tree synced.', ephemeral=True)

@bot.command(name='clear_commands', description='Owner only')
@commands.is_owner()
async def unsync(ctx):
    MY_GUILD = discord.Object(id=GUILD)
    bot.tree.clear_commands(guild=None)
    bot.tree.clear_commands(guild=MY_GUILD)
    await ctx.send('Command tree cleared.', ephemeral=True)

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