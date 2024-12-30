# bot.py
import discord
from discord.ext import commands
from config import TOKEN, SharedState
from helpers.category_utils import calculate_uptime
from helpers.redis_utils import populate_events_vars

start_time = 0
uptime = 0

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    uptime = calculate_uptime()
    bot_date = SharedState.read_date()
    populate_events_vars()
    print(f'Bot\'s current date is {bot_date}. Current uptime: {uptime} (Uptime is used to decide when to advance the calendar in Auto mode.)')

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