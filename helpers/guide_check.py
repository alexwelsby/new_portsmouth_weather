import discord
from discord import app_commands

def is_guide():
        #checks if the user has the GUIDE role
        async def predicate(interaction: discord.Interaction) -> bool:
            guide_role = discord.utils.get(interaction.user.roles, name="GUIDE")
            return guide_role is not None
        return app_commands.check(predicate)