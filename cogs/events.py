from discord.ext import commands
import discord
import io
from helpers.event_builder import generate_json_event
from helpers.redis_utils import remove_from_redis,get_event_json, json_loads, add_to_redis
from config import SharedState

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
    @commands.has_role('GUIDE')
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

    @commands.command(name='end_event', help='Creates an event that takes the following parameters: start_date:<YYYY:MM:DD> max_temp:<#> min_temp:<#> max_precipitation:<#> min_precipitation:<#> time_period:<day|week|month> max_cloud_cover:<%> min_cloud_cover:<%> chance_rain:<%> chance_snow:<%>')
    @commands.has_role('GUIDE')
    async def end_current_event(self, ctx, args_redis_key:str):
        outcome = remove_from_redis(args_redis_key)
        await ctx.send(outcome)

    @commands.command(name='list_events', help='Creates an event that takes the following parameters: start_date:<YYYY:MM:DD> max_temp:<#> min_temp:<#> max_precipitation:<#> min_precipitation:<#> time_period:<day|week|month> max_cloud_cover:<%> min_cloud_cover:<%> chance_rain:<%> chance_snow:<%>')
    @commands.has_role('GUIDE')
    async def list_events(self, ctx):
        all_events = SharedState.get_events()
        print(f"all events? {all_events}")
        await ctx.send(all_events)

    @commands.command(name='download_event', help='Creates an event that takes the following parameters: start_date:<YYYY:MM:DD> max_temp:<#> min_temp:<#> max_precipitation:<#> min_precipitation:<#> time_period:<day|week|month> max_cloud_cover:<%> min_cloud_cover:<%> chance_rain:<%> chance_snow:<%>')
    @commands.has_role('GUIDE')
    async def download_event(self, ctx, args_redis_key:str):
        print("HALP")
        json = get_event_json(args_redis_key)
        print(json)
        if json == None:
            await ctx.send("No event found at that key. Did you misspell it? Use !list_events to double-check all available keys.")
        else:
            #no disk usage for this, just in-memory?
            with io.StringIO() as file:
                file.write(json)
                file.seek(0) #resetting the file buffer to the start
                json_file = discord.File(file, filename=f"{args_redis_key}.json")
                await ctx.send(f"Json file found for {args_redis_key} - and now, the weather.", file=json_file)

    @commands.command(name='overwrite_event', help='Creates an event that takes the following parameters: start_date:<YYYY:MM:DD> max_temp:<#> min_temp:<#> max_precipitation:<#> min_precipitation:<#> time_period:<day|week|month> max_cloud_cover:<%> min_cloud_cover:<%> chance_rain:<%> chance_snow:<%>')
    @commands.has_role('GUIDE')
    async def overwrite_event(self, ctx, args_redis_key:str):
        found = False
        for event in SharedState.all_events:
            print(event.event_redis_key)
            if event.event_redis_key == args_redis_key:
                found = True
        if not found:
            await ctx.send("ERROR: The event key you passed does not exist as an Event in the Redis database. This command is intended for overwriting and fine-tuning existing events that are already in the database, not creating new events. Please use !create_event with your desired parameters first.")
            return
        
        if not ctx.message.attachments:
            await ctx.send("ERROR: You forgot to attach a .json file to this command.")
            return
        #getting the first attachment - could change this to allow bulk attachments later
        attachment = ctx.message.attachments[0]
        if not attachment.filename.endswith('.json'):
            await ctx.send("ERROR: The attached file is not a .json. Please attach a .json file.")
            return
        
        file_content = await attachment.read()
        response = add_to_redis(args_redis_key, json_loads(file_content))
        await ctx.send(response)
        



async def setup(bot):
    await bot.add_cog(events(bot))