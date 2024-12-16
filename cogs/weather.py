import discord
from discord.ext import commands
from helpers.weather_utils import build_weatherman, create_embed, get_current_json
from global_state import bot_date

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.time_period = 'week'

    @commands.group(invoke_without_command=True)
    async def weather(self, ctx):
        await ctx.send("Available subcommands: report <day|week>, set_date <date>, get_date.")

    @weather.command(name='report', help='Gets current weather for New Portsmouth.')
    async def report(self, ctx, args_time_period: str):
        try:
            self.time_period = args_time_period
            async with ctx.typing():
                global bot_date
                result = get_current_json(bot_date, self.time_period)
                if result:
                    data, report = build_weatherman(result, self.time_period)
                    embed = create_embed(data, report, ctx)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"No event found for {bot_date}.")
        except Exception as e:
            await ctx.send(f"Error fetching data: {e}")

async def setup(bot):
    await bot.add_cog(Weather(bot))