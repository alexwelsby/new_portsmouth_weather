from discord.ext import commands
from dateutil.parser import parse
from config import SharedState

class date_management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='set_date', help='Set the current date of the weather bot. (In auto mode, it will begin counting up from this date.)')
    async def set_date(self, ctx, *, date:str):
        async with ctx.typing():
            try:
                dt = parse(date)
                SharedState.write_date(dt.strftime('%Y-%m-%d'))
                response = f"((OOC: My date has been set to {SharedState.bot_date} (YYYY-MM-DD).))"
                await ctx.send(response)
            except Exception as e:
                await ctx.send(f"Error setting date: {e}")

    @commands.command(name='get_date', help='Get the current date of the weather bot.')
    async def get_date(self, ctx):
        async with ctx.typing():
            response = f"((OOC: My current date is {SharedState.bot_date} (YYYY-MM-DD).))"
            await ctx.send(response)

async def setup(bot):
    await bot.add_cog(date_management(bot))