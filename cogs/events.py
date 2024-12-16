from discord.ext import commands
from helpers.json_builder import generate_json_event

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
        
    @commands.command(name='create_event', help='Creates an event that takes the following parameters: start_date:<YYYY:MM:DD> max_temp:<#> min_temp:<#> max_precipitation:<#> min_precipitation:<#> time_period:<day|week|month> max_cloud_cover:<%> min_cloud_cover:<%> chance_rain:<%> chance_snow:<%>')
    async def create_event(self, ctx, *args):
        params_list = self.params_list
        for arg in args:
            if ':' not in arg:
                await ctx.send("Invalid arguments list provided. Expecting at least one argument.")
                return

            key, value = arg.split(':', 1)
            if key in params_list:
                if key not in ['start_date', 'time_period']:
                    try:
                            params_list[key] = float(value)
                    except ValueError:
                        await ctx.send(f"Invalid numeric value for {key}. Please provide a valid number.")
                        return
                else:
                    params_list[key] = value
            else:
                await ctx.send(f"Unknown parameter: {key}")
                return

            # Validate required parameters
        if params_list['max_temp'] is None or params_list['min_temp'] is None:
            await ctx.send("Error: max_temp or min_temp is not set.")
            return

        errors = ""
        if params_list['max_temp'] <= params_list['min_temp']:
            errors += "Error: max_temp must be greater than min_temp.\n"

        if params_list['max_precipitation'] < params_list['min_precipitation']:
            errors += "Error: max_precipitation must be greater than or equal to min_precipitation.\n"

        if errors:
            await ctx.send(errors)
            return
        else:
            generate_json_event(params_list)
            await ctx.send(f"Weather event created with max-temp: {params_list['max_temp']} and min-temp: {params_list['min_temp']}")

async def setup(bot):
    await bot.add_cog(events(bot))