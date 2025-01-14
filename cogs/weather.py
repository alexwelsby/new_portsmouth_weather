from discord.ext import commands
import discord
from discord import app_commands
from config import SharedState, LOCATION
from helpers.weatherman_utils import build_weatherman, create_embed, debug_descriptions
from helpers.redis_utils import get_current_json
from helpers.category_utils import get_unix_date
import io, discord

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #parent group for weatherbot commands
    """@commands.group(invoke_without_command=True)
    async def weather(self, ctx):
        await ctx.send("Available subcommands: report <day|week>, set_date <date>, get_date. Use '!weather <subcommand> <optional:args>'.")"""

    @app_commands.command(name='create_event', description='Creates a weather event with the given parameters and puts it in the redis database.')
    @app_commands.describe(args_time_period="<today|day|week|month>")
    async def report(self, interaction: discord.Interaction, args_time_period:str):
        if args_time_period == "today":
            args_time_period = "day"
        SharedState.time_period = args_time_period
        try:
            async with interaction.channel.typing():
                bot_date = SharedState.read_date()
                event_key = SharedState.check_if_event(bot_date) #returns either the key or none
                result = get_current_json(bot_date, event_key, args_time_period)
                if result != "":
                    data, report = build_weatherman(result, args_time_period)
                    embed = create_embed(data, report, ctx)
                    await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message(f"No event found for {bot_date}.", empheral=True)
        except Exception as e:
            await interaction.response.send_message(f"Error blowing up data: {e}", empheral=True)

    @commands.command(name='debug_list_reports', help='Lists all possible single weather report strings.')
    @commands.has_role('GUIDE')
    async def debug_list_reports(self, ctx):
        try:
            async with ctx.typing():
                all_reports = debug_descriptions()
                with io.StringIO() as file:
                    file.write(all_reports)
                    file.seek(0) #resetting the file buffer to the start
                    txt_file = discord.File(file, filename=f"debug_descriptions.txt")
                    await ctx.send(f"Here's a txt file of all possible weather reports, with placeholder info.", file=txt_file)
        except Exception as e:
            await ctx.send(f"Error blowing up data: {e}")

async def setup(bot):
    await bot.add_cog(Weather(bot))