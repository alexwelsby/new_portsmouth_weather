from discord.ext import commands
import discord
from discord import app_commands
import io
from typing import Optional
from dateutil.parser import parse
from datetime import datetime
from helpers.event_builder import generate_json_event, get_start_end, add_event
from helpers.redis_utils import remove_from_redis,get_event_json, json_loads, add_to_redis
from config import SharedState
from helpers.guide_check import is_guide

class events(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

        
    @app_commands.command(name='create_event', description='Creates a weather event with the given parameters and puts it in the redis database.')
    @app_commands.describe(start_date="<YYYY/MM/DD>",time_period="<day|week|month>", chance_rain="<Percent chance for rain on a given day>", 
                           chance_snow="<Percent chance for snow on a given day>",
                           max_temp="<Minimum temperature in Fahrenheit>", 
                           min_temp="<Maximum temperature in Fahrenheit>", 
                           min_precipitation="<Minimum precipitation in inches>", 
                           max_precipitation="<Maximum precipitation in inches>", 
                           min_cloud_cover="<Minimum percent of sky covered by clouds>",
                           max_cloud_cover="<Maximum percent of sky covered by clouds>",
                           min_humidity="<Minimum percent of humidity on a given day>",
                           max_humidity="<Maximum percent of humidity on a given day>",
                           min_windspeed="<Minimum windspeed in MPH on a given day>",
                           max_windspeed="<Maximum windspeed in MPH on a given day>",)
    @is_guide()
    async def create_event(self, 
        interaction: discord.Interaction,
        start_date: str,
        time_period: Optional[str] = "month",
        max_temp: Optional[float] = None,
        min_temp: Optional[float] = None,
        min_precipitation: Optional[float] = None,
        max_precipitation: Optional[float] = None,
        min_cloud_cover: Optional[float] = None,
        max_cloud_cover: Optional[float] = None,
        chance_rain: Optional[float] = None,
        chance_snow: Optional[float] = None,
        min_humidity:Optional[float] = None,
        max_humidity: Optional[float] = None,
        min_windspeed: Optional[float] = None,
        max_windspeed: Optional[float] = None,
        ):
        start_date = parse(start_date).strftime('%Y-%m-%d')
        params_list =  {
            'start_date': start_date,
            'time_period': time_period,
            'chance_rain': chance_rain,
            'chance_snow': chance_snow,
            'min_temp': min_temp,
            'max_temp': max_temp,
            'min_precipitation': min_precipitation,
            'max_precipitation': max_precipitation,
            'min_cloud_cover': min_cloud_cover,
            'max_cloud_cover': max_cloud_cover,
            'min_humidity': min_humidity,
            'max_humidity': max_humidity,
            'min_wind_speed': min_windspeed,
            'max_wind_speed': max_windspeed,
        }
        errors = ""

        keys = list(params_list.keys())[4:] #where the min/max pairs start
        #i've considered using ranges instead but the pairs allow people to really fine-tune the historical data (ex, leaving max-humidity out but not min-humidity)
        for i in range(0, len(keys), 2):
            min_key = keys[i]
            max_key = keys[i + 1]
            min_value = params_list[min_key]
            max_value = params_list[max_key]

            if min_value is not None and max_value is not None and min_value > max_value:
                errors += f"Error: {max_key} must be greater than or equal to {min_key}.\n"

        if errors:
            await interaction.response.send_message(errors)
            return
        else:
            generate_json_event(params_list)
            await interaction.response.send_message(f"Weather event created with the following parameters: {params_list}. \n Please note that any undeclared parameters have been filled in with historical weather data from a nearby location.", ephemeral=True)
            return

    @app_commands.command(name='remove_event', description='Deletes the event with the given redis key.')
    @app_commands.describe(redis_key="The redis key of the event (If you don't know of any keys, use /list_events to see all keys.)")
    @is_guide()
    async def remove_event(self,  interaction: discord.Interaction, redis_key:str):
        response = remove_from_redis(redis_key)
        pop_response = SharedState.remove_event(SharedState, redis_key)
        if pop_response == None:
            pop_response = "No such key found in the bot's memory."
        else:
            pop_response = f"{redis_key} successfully removed from bot memory."
        await interaction.response.send_message(response + "\n" + pop_response, ephemeral=True)
        return

    @app_commands.command(name='list_events', description='Lists all currently scheduled events with their keys and unix start and end times.')
    @is_guide()
    async def list_events(self, interaction: discord.Interaction):
        all_events = SharedState.all_events
        if len(all_events) > 0:
            embed = self.create_event_embed(all_events, interaction)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        else:
            s = 'No events found. Try using /create_event to create a new weather event.'
            await interaction.response.send_message(s, ephemeral=True)
            return
    
    @app_commands.command(name='get_current_event', description='Gets the Redis key of the current event.')
    @is_guide()
    async def get_current_event(self, interaction: discord.Interaction):
        redis_key = SharedState.get_current_event()
        if redis_key == None:
            await interaction.response.send_message("There's no event currently running.", ephemeral=True)
            return
        else:
            await interaction.response.send_message(f"The currently-running event has the key {redis_key}. Run /download_event {redis_key} to see its data, or /remove_event {redis_key} to end it.", ephemeral=True)
            return
    
    @app_commands.command(name='end_current_event', description='Ends the event that\'s occurring now, if there is one.')
    @is_guide()
    async def end_current_event(self, interaction: discord.Interaction):
        redis_key = SharedState.end_current_event()
        if redis_key == None:
            await interaction.response.send_message("There's no event currently running.", ephemeral=True)
            return
        else:
            response = remove_from_redis(redis_key)
            if response == None:
                await interaction.response.send_message(f"{redis_key} deleted from bot memory, but not found in redis. Something went wonky...", ephemeral=True)
                return
            else: 
                await interaction.response.send_message(f"{redis_key} has been deleted from bot memory and redis - it will trouble you no more.",ephemeral=True)
                return
        
        

    @app_commands.command(name='download_event', description='Downloads the raw data of the event at the given redis key.')
    @app_commands.describe(redis_key="The redis key of the event (If you don't know of any keys, use /list_events to see all keys.)")
    @is_guide()
    async def download_event(self, interaction: discord.Interaction, redis_key:str):
        json = get_event_json(redis_key)
        if json == None:
            await interaction.response.send_message("No event found at that key. Did you misspell it? Use !list_events to double-check all available keys.", ephemeral=True)
        else:
            #no disk usage for this, just in-memory?
            with io.StringIO() as file:
                file.write(json)
                file.seek(0) #resetting the file buffer to the start
                json_file = discord.File(file, filename=f"{redis_key}.json")
                await interaction.response.send_message(f"Json file found for {redis_key}: and now, the weather.",ephemeral=True, file=json_file)
                return

    @app_commands.command(name='overwrite_event', description='Upload a .json attachment to replace a given event\'s raw data.')
    @app_commands.describe(redis_key="The redis key of the event (If you don't know of any keys, use /list_events to see all keys.)")
    @is_guide()
    async def overwrite_event(self, interaction: discord.Interaction, redis_key:str):
        found_event = SharedState.get_event(redis_key)
        if found_event == None:
            await interaction.response.send_message("ERROR: The event key you passed does not exist as an Event in the Redis database. This command is intended for overwriting and fine-tuning existing events that are already in the database, not creating new events. Please use !create_event with your desired parameters first.", ephemeral=True)
            return
        
        async for message in interaction.channel.history(limit=10):
            if message.author == interaction.user and message.attachments:
                attachment = message.attachments[0]
            if not attachment:
                await interaction.response.send_message("ERROR: You forgot to send a json file before running this command.", ephemeral=True)
                return
        #getting the first attachment - could change this to allow bulk attachments later

            if not attachment.filename.endswith('.json'):
                await interaction.response.send_message("ERROR: The attached file is not a .json. Please attach a .json file.",ephemeral=True)
                return
        
            file_content = await attachment.read()
            json = json_loads(file_content)
            response = add_to_redis(redis_key, json)
            start, end = get_start_end(json)
            add_event(redis_key, start, end)
            await interaction.response.send_message(response,ephemeral=True)
            return
        
    def create_event_embed(self, all_events, interaction):
        title = "All scheduled events:"
        embed = discord.Embed(title=title,
            color=interaction.guild.me.top_role.color,
            timestamp=discord.utils.utcnow(),)
        for event in all_events.values():
            date_start = datetime.fromtimestamp(event.get_start()).strftime('%Y-%m-%d')
            date_end = datetime.fromtimestamp(event.get_end()).strftime('%Y-%m-%d')
            embed.add_field(name="Redis Key", value=f"{event.get_key()}", inline=True)
            embed.add_field(name="Start Time", value=f"{date_start}", inline=True)
            embed.add_field(name="End Time", value=f"{date_end}", inline=True)

        embed.set_footer(text=f"Requested by {interaction.user.name}")
        return embed
        



async def setup(bot):
    await bot.add_cog(events(bot))