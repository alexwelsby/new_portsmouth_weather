from discord.ext import commands
from config import SharedState, LOCATION
from helpers.weatherman_utils import build_weatherman, create_embed
from helpers.redis_utils import get_current_json
from helpers.category_utils import get_unix_date

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #parent group for weatherbot commands
    """@commands.group(invoke_without_command=True)
    async def weather(self, ctx):
        await ctx.send("Available subcommands: report <day|week>, set_date <date>, get_date. Use '!weather <subcommand> <optional:args>'.")"""

    @commands.command(name='report', help='Gets current weather for New Portsmouth.')
    async def report(self, ctx, args_time_period:str):
        if args_time_period == "today":
            args_time_period = "day"
        SharedState.time_period = args_time_period
        try:
            async with ctx.typing():
                event_key = check_if_event() #returns either the key or none
                result = get_current_json(SharedState.bot_date, event_key, SharedState.time_period)
                if result != "":
                    data, report = build_weatherman(result)
                    embed = create_embed(data, report, ctx)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"No event found for {SharedState.bot_date}.")
        except Exception as e:
            await ctx.send(f"Error blowing up data: {e}")

def check_if_event():
    unix_date = get_unix_date(SharedState.read_date())
    if (len(SharedState.all_events) > 0):
        for event in SharedState.all_events:
            if unix_date > event.start_unix and unix_date < event.end_unix:
                print(f"event found; redis key {event.event_redis_key}")
                return event.event_redis_key
    return None
    


async def setup(bot):
    await bot.add_cog(Weather(bot))