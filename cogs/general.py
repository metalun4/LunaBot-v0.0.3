from discord.ext import commands
import discord
import time
import requests
import aiohttp
import sys
import os
from textwrap import dedent
from utils import presence, settings
import psutil
import logging
import traceback


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_bot_uptime(self, start_time):
        t = time.gmtime(time.time() - start_time)
        return f"{t.tm_mday - 1} days, {t.tm_hour} hours, and {t.tm_min} minutes"

    @commands.cooldown(rate=1, per=3)
    @commands.command()
    async def info(self, ctx):
        async with ctx.channel.typing():
            e = discord.Embed(
                color=discord.Color(0x6441A4),
                title="Luna Bot | Discord Bot For Gaming Community"
            )
            uptime = self.get_bot_uptime(self.bot.uptime)
            mem = psutil.virtual_memory()
            e.add_field(
                name="Uptime",
                value=uptime,
                inline=False
            )
            e.add_field(
                name="Version",
                value=dedent(f"""\
                    **·** Python {sys.version.split(' ')[0]}
                    **·** discord.py {discord.__version__}
                    **·** Luna Bot {settings.Version}
                    """)
            )
            if ctx.guild is None:
                e.add_field(
                    name="Shard Info",
                    value=dedent(f"""\
                        **·** Shard latency: {round(self.bot.latency*1000)}ms
                        **·** Total shards: {self.bot.shard_count}
                        """)
                )
            else:
                e.add_field(
                    name="Shard Info",
                    value=dedent(f"""\
                        **·** Current shard: {ctx.guild.shard_id}
                        **·** Shard latency: {round(self.bot.latency*1000)}ms
                        **·** Total shards: {self.bot.shard_count}
                        """)
                )
            e.add_field(
                name="System",
                value=dedent(f"""\
                    **·** {psutil.cpu_percent(interval=1)}% CPU
                    **·** {round(mem.used/1000000)}/{round(mem.total/1000000)}MB RAM used
                    """)
            )
            e.add_field(
                name="Developer",
                value="MetaLuna#1999",
                inline=False
            )
            await ctx.send(embed=e)

    @commands.cooldown(rate=1, per=3)
    @commands.command(pass_context=True)
    async def ping(self, ctx):
        t = time.time()
        await ctx.trigger_typing()
        t2 = round((time.time() - t) * 1000)
        await ctx.send("Pong! {}ms".format(t2))

    @commands.command(pass_context=True)
    async def invite(self, ctx):
        await ctx.send("https://discordapp.com/api/oauth2/authorize?scope=bot&permissions=8&client_id=272451861636841482")


def setup(bot):
    bot.add_cog(General(bot))
