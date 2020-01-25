import asyncio
import discord
from . import settings


async def change_presence(bot):
    if settings.UseBetaBot:
        await bot.change_presence(status=discord.Status.idle, activity=discord.Game("with new features"))
    else:
        await bot.change_presence(activity=discord.Game(name="!luna help"))