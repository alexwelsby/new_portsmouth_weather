import discord
from discord import app_commands
from config import ADMIN_ROLE

def is_guide():
        async def predicate(interaction: discord.Interaction) -> bool:
            guide_role = discord.utils.get(interaction.user.roles, name=ADMIN_ROLE)
            return guide_role is not None
        return app_commands.check(predicate)