from discord.ext import commands
from discord import app_commands
import discord
from dateutil.parser import parse
from config import SharedState

class date_management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_guide():
        #checks if the user has the GUIDE role
        async def predicate(interaction: discord.Interaction) -> bool:
            guide_role = discord.utils.get(interaction.user.roles, name="GUIDE")
            return guide_role is not None
        return app_commands.check(predicate)

    @app_commands.command(name='set_date', description='Sets the current date of the weather bot.')
    @app_commands.describe(date="The new date to set (e.g., YYYY-MM-DD or 'November 23 2023'. (Keep in mind valid dates fall between 2022-12-31 and 2024-12-07.)")
    @is_guide()
    async def set_date(self, interaction: discord.Interaction, date:str):
        async with interaction.channel.typing():
            try:
                dt = parse(date)
                SharedState.write_date(dt.strftime('%Y-%m-%d'))
                response = f"((OOC: My date has been set to {SharedState.bot_date} (YYYY-MM-DD).))"
                await interaction.response.send_message(response)
            except Exception as e:
                await interaction.response.send_message(f"Error setting date: {e}")

    @app_commands.command(name='get_date', description='Get the current date of the weather bot.')
    @is_guide()
    async def get_date(self, interaction: discord.Interaction):
        date = SharedState.read_date()
        response = f"((OOC: My current date is {date} (YYYY-MM-DD).))"
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
            response = f"((OOC: Date has been rolled over. My current date is {date} (YYYY-MM-DD). {event_happening.format(key=key)}))"
            await interaction.response.send_message(response)

async def setup(bot):
    await bot.add_cog(date_management(bot))