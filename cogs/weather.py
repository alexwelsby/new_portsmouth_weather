from discord.ext import commands
from config import SharedState, LOCATION
from helpers.weatherman_utils import build_weatherman, create_embed, get_current_json

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #parent group for weatherbot commands
    """@commands.group(invoke_without_command=True)
    async def weather(self, ctx):
        await ctx.send("Available subcommands: report <day|week>, set_date <date>, get_date. Use '!weather <subcommand> <optional:args>'.")"""

    @commands.command(name='report', help='Gets current weather for New Portsmouth.')
    async def report(self, ctx, args_time_period:str):
        SharedState.time_period = args_time_period
        try:
            async with ctx.typing():
                result = get_current_json(SharedState.bot_date, SharedState.time_period)
                if result != "":
                    data, report = build_weatherman(result)
                    embed = create_embed(data, report, ctx)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"No event found for {SharedState.bot_date}.")
        except Exception as e:
            await ctx.send(f"Error blowing up data: {e}")

async def setup(bot):
    await bot.add_cog(Weather(bot))