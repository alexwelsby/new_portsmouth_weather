from discord.ext import commands
from bot import weather

class events(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    params_list =  {
        'start_date': "2023-02-01",
        'time_period': "week",
        'max_temp': 0.0,
        'min_temp': 0.0,
        'max_precipitation': 0.0,
        'min_precipitation': 0.0,
        'max_cloud_cover': 0.0,
        'min_cloud_cover': 0.0,
        'chance_rain': 0.0,
        'chance_snow': 0.0,
    }
        
    @commands.command(name='create_event', help='Creates an event that takes the following parameters: start_date:<YYYY:MM:DD> max_temp:<#> min_temp:<#> max_precipitation:<#> min_precipitation:<#> time_period:<day|week|month> max_cloud_cover:<%> min_cloud_cover:<%> rain:<%> clouds:<%>')
    async def create_event(self, ctx, *args):
        params_list = self.params_list
        async with ctx.typing():
            for arg in args:
                print(arg)
                if ':' in arg:
                    key, value = arg.split(':', 1)  
                    if key in params_list:
                        params_list[key] = float(value)
                else:
                    await ctx.send("Invalid arguments list provided. Expecting at least one argument.")
            print(params_list['max_temp'])
            errors = ""
            if params_list['max_temp'] < params_list['min_temp'] or params_list['max_temp'] == params_list['min_temp']:
                errors += "Error: You have either not set max_temp and min_temp, or you have set max_temp to be less than min_temp. \n"
                print(errors)

            if params_list['max_precipitation'] < params_list['min_precipitation']:
                errors += "Error: You have set max_precipitation to be less than min_precipitation. \n"
                print(errors)
            
            total_percent = params_list['clouds'] + params_list['clear'] + params_list['rain'] + params_list['snow']
            print("total", total_percent)
            if total_percent < 100.0:
                errors += f"Error: clouds:{params_list['clouds']} clear:{params_list['clear']} rain:{params_list['rain']} snow:{params_list['snow']} adds up to {total_percent}%, not 100.0%."
            
            if errors != "":
                await ctx.send(errors)
            else:
                await ctx.send(f"Weather event created with max-temp: {params_list['max_temp']} and min-temp: {params_list['min_temp']}")

async def setup(bot):
    await bot.add_cog(events(bot))