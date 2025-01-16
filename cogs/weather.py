from discord.ext import commands
import discord
from discord import app_commands
from config import SharedState
from helpers.weatherman_utils import build_weatherman, create_embed, debug_descriptions
from helpers.redis_utils import get_current_json
import io, discord
from helpers.guide_check import is_guide

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='weather_report', description='Creates a weather event with the given parameters and puts it in the redis database.')
    @app_commands.describe(time_period="<today|day|week|month>")
    async def report(self, interaction: discord.Interaction, time_period:str):
        if time_period == "today":
            time_period = "day"
        SharedState.time_period = time_period
        try:
            async with interaction.channel.typing():
                bot_date = SharedState.read_date()
                event_key = SharedState.check_if_event(bot_date) #returns either the key or none
                result = get_current_json(bot_date, event_key, time_period)
                if result != "":
                    data, report = build_weatherman(result, time_period)
                    embed = create_embed(data, report, interaction)
                    await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message(f"No event found for {bot_date}.", empheral=True)
        except Exception as e:
            await interaction.response.send_message(f"Error blowing up data: {e}", empheral=True)

    @app_commands.command(name='debug_list_reports', description='Lists ALL POSSIBLE weather reports given all possible weather \'categories\' in a LONG txt file.')
    @is_guide()
    async def debug_list_reports(self, interaction: discord.Interaction):
        try:
            async with interaction.channel.typing():
                all_reports = debug_descriptions()
                with io.StringIO() as file:
                    file.write(all_reports)
                    file.seek(0) #resetting the file buffer to the start
                    txt_file = discord.File(file, filename=f"debug_descriptions.txt")
                    await interaction.response.send_message(f"Here's a txt file of all possible weather reports, with placeholder info.", ephemeral=True, file=txt_file)
                    return
        except Exception as e:
            await interaction.response.send_message(f"Error blowing up data: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Weather(bot))