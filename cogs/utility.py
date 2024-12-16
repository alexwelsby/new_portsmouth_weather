import discord
from discord.ext import commands
from datetime import datetime

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.now()
    
    @commands.command(name='uptime', help='Shows how long the weather bot has been running.')
    async def getUptime(self, ctx):
        current_time = datetime.now()
        uptime = current_time - self.start_time
        days, seconds = uptime.days, uptime.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        await ctx.send(f"Uptime: {days}d {hours}h {minutes}m {seconds}s.")

async def setup(bot):
    await bot.add_cog(Utility(bot))