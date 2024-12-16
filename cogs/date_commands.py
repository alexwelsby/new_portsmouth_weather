import discord
from discord.ext import commands
from dateutil.parser import parse

class date_commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='set_date', help='Sets the current date of the weather bot.')
    async def set_date(self, ctx, *, date:str):
        