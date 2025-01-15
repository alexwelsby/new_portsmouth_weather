from discord.ext import commands
import discord
from discord import app_commands
from helpers.category_utils import calculate_uptime
from helpers.guide_check import is_guide

class Uptime(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @app_commands.command(name='uptime', description="Gets the current running uptime of the bot.")
    @is_guide()
    async def get_uptime(self, interaction: discord.Interaction):
        async with interaction.channel.typing():
            days, hours, minutes, seconds = calculate_uptime()
            formatted_uptime = f"Uptime: {days}d {hours}h {minutes}m {seconds}s."
            await interaction.response.send_message(formatted_uptime)

async def setup(bot):
    await bot.add_cog(Uptime(bot))