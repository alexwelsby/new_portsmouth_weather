from discord.ext import commands
import discord
from discord import app_commands
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

    #duplicate code but it's nearly midnight.
    def is_guide():
        #checks if the user has the GUIDE role
        async def predicate(interaction: discord.Interaction) -> bool:
            guide_role = discord.utils.get(interaction.user.roles, name="GUIDE")
            return guide_role is not None
        return app_commands.check(predicate)
        
    #fix this
    @app_commands.command(name='create_event', description='Creates a weather event with the given parameters and puts it in the redis database.')
    @app_commands.describe(start_date="<YYYY/MM/DD>", time_period="<day|week|month>", max_temp="<# in degrees F>", min_temp="<# in degrees F>", min_precipitation="<# in inches>", max_precipitation="<# in inches>", min_cloud_cover="<%>", max_cloud_cover="<%>", chance_rain="%", chance_snow="<%>")
    @is_guide()
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

    @app_commands.command(name='remove_event', description='Deletes the event with the given redis key.')
    @app_commands.describe(args_redis_key="The redis key of the event (If you don't know of any keys, use /list_events to see all keys.)")
    @is_guide()
    async def remove_event(self,  interaction: discord.Interaction, args_redis_key:str):
        response = remove_from_redis(args_redis_key)
        await interaction.response.send_message(response)

    @app_commands.command(name='list_events', description='Lists all currently scheduled events with their keys and unix start and end times.')
    @is_guide()
    async def list_events(self, interaction: discord.Interaction):
        all_events = SharedState.get_events()
        await interaction.response.send_message(all_events)

    @app_commands.command(name='download_event', description='Downloads the raw data of the event at the given redis key.')
    @app_commands.describe(args_redis_key="The redis key of the event (If you don't know of any keys, use /list_events to see all keys.)")
    @is_guide()
    async def download_event(self, interaction: discord.Interaction, args_redis_key:str):
        json = get_event_json(args_redis_key)
        print(json)
        if json == None:
            await interaction.response.send_message("No event found at that key. Did you misspell it? Use !list_events to double-check all available keys.")
        else:
            #no disk usage for this, just in-memory?
            with io.StringIO() as file:
                file.write(json)
                file.seek(0) #resetting the file buffer to the start
                json_file = discord.File(file, filename=f"{args_redis_key}.json")
                await interaction.response.send_message(f"Json file found for {args_redis_key} - and now, the weather.", file=json_file)

    @commands.command(name='overwrite_event', help='Upload a .json attachment to replace a given event\'s raw data. (WARNING: MAKE SURE YOU KNOW WHAT YOU\'RE DOING! YOU CAN BREAK YOUR EVENT.)')
    @app_commands.describe(args_redis_key="The redis key of the event (If you don't know of any keys, use /list_events to see all keys.)")
    @is_guide()
    async def overwrite_event(self,  interaction: discord.Interaction, args_redis_key:str):
        found = False
        for event in SharedState.all_events:
            print(event.event_redis_key)
            if event.event_redis_key == args_redis_key:
                found = True
        if not found:
            await interaction.response.send_message("ERROR: The event key you passed does not exist as an Event in the Redis database. This command is intended for overwriting and fine-tuning existing events that are already in the database, not creating new events. Please use !create_event with your desired parameters first.")
            return
        
        async for message in interaction.channel.history(limit=10):
            if message.author == interaction.user and message.attachments:
                attachment = message.attachments[0]

            if not attachment:
                await interaction.response.send_message("ERROR: You forgot to attach a .json file to this command.")
                return
        #getting the first attachment - could change this to allow bulk attachments later

            if not attachment.filename.endswith('.json'):
                await interaction.response.send_message("ERROR: The attached file is not a .json. Please attach a .json file.")
                return
        
            file_content = await attachment.read()
            response = add_to_redis(args_redis_key, json_loads(file_content))
            await interaction.response.send_message(response)
        



async def setup(bot):
    await bot.add_cog(events(bot))