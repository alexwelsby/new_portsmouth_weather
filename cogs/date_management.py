import discord
from discord.ext import commands
from discord import app_commands
from dateutil.parser import parse
from config import SharedState
from helpers.guide_check import is_guide

class date_management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='set_date', description='Sets the current date of the weather bot.')
    @app_commands.describe(date="The new date to set (e.g., YYYY-MM-DD or 'November 23 2023'. (Keep in mind valid dates fall between 2022-12-31 and 2024-12-07.)")
    @is_guide()
    async def set_date(self, interaction: discord.Interaction, date:str):
        async with interaction.channel.typing():
            try:
                dt = parse(date)
                SharedState.write_date(dt.strftime('%Y-%m-%d'))
                response = f"My date has been set to {SharedState.bot_date} (YYYY-MM-DD)."
                await interaction.response.send_message(response)
            except Exception as e:
                await interaction.response.send_message(f"Error setting date: {e}")

    @app_commands.command(name='get_date', description='Get the current date of the weather bot.')
    @is_guide()
    async def get_date(self, interaction: discord.Interaction):
        date = SharedState.read_date()
        response = f"My current date is {date} (YYYY-MM-DD)."
        await interaction.response.send_message(response)

    @app_commands.command(name='rollover_date', description='Advances the date by one day.')
    @is_guide()
    async def rollover_date(self, interaction: discord.Interaction):
        async with interaction.channel.typing():
            key = SharedState.check_if_event(SharedState.bot_date)
            date = SharedState.rollover_date()
            event_happening = 'There is no active weather event. Use /create_event if you\'d like an event for this date.'
            if (key != None):
                event_happening = "I'm currently trying to stay within a mod-set weather event. The key of the event is {key}; use !download_event {key} if you'd like to see the raw data, or !end_event {key} if you'd like the event to end."
            response = f"Date has been rolled over. My current date is {date} (YYYY-MM-DD). {event_happening.format(key=key)}"
            await interaction.response.send_message(response)

async def setup(bot):
    await bot.add_cog(date_management(bot))