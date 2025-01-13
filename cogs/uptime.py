from discord.ext import commands
from helpers.category_utils import calculate_uptime

class Uptime(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.command(name='uptime', help='Shows the current uptime of the weatherbot.')
    @commands.has_role('GUIDE')
    async def get_uptime(self, ctx):
        async with ctx.typing():
            days, hours, minutes, seconds = calculate_uptime()
            formatted_uptime = f"((OOC: Uptime: {days}d {hours}h {minutes}m {seconds}s.))"
            await ctx.send(formatted_uptime)

async def setup(bot):
    await bot.add_cog(Uptime(bot))