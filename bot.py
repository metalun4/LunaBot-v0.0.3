import discord, asyncio
import logging, traceback
import platform
import time
import sys

from discord.ext import commands
from utils import presence,settings


log = logging.getLogger("bot.core")


class LunaBot(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uptime = 0
        self.add_command(self.__reload__)
        modules = [
            "cogs.general",
            "cogs.pug"
        ]
        for m in modules:
            try: self.load_extension(m)
            except: log.error(f"Failed to load {m}:\n{traceback.format_exc()}")
            else: log.debug(f"Loaded {m}")
        log.info(f"Loaded {len(modules)} modules")

    async def on_ready(self):
        await presence.change_presence(self)
        print(f"discord.py version: {discord.__version__}")
        print(f"Python version: {platform.python_version()}")
        print(f"Running on: {platform.system()} v{platform.version()}")
        print(f"Discord user: {self.user} / {self.user.id}")
        print(f"Connected guilds: {len(self.guilds)}")
        print(f"Connected users: {len(list(self.get_all_members()))}")
        print(f"Shard IDs: {getattr(self, 'shard_ids', None)}")
        self.uptime = time.time()

    async def on_command(self, ctx):
        if ctx.author.bot:
            return

        commands.Cooldown(1, 5, commands.BucketType.user).update_rate_limit()

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send(ctx.message.author, 'This command cannot be used in private messages.')
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send(ctx.message.author, 'Sorry. This command is disabled and cannot be used.')
        elif isinstance(error, commands.CommandInvokeError):
            print('In {0.command.qualified_name}:'.format(ctx), file=sys.stderr)
            traceback.print_tb(error.original.__traceback__)
            print('{0.__class__.__name__}: {0}'.format(error.original), file=sys.stderr)
        # -- Unhandled exceptions -- #
        logging.fatal(f"{type(error).__name__}")

    @commands.command(hidden=True, name="reload")
    async def __reload__(ctx, cog):
        if not ctx.author.id in settings.BotOwners: return
        try:
            ctx.bot.unload_extension(cog)
            ctx.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f"Failed to reload cog: `{type(e).__name__}: {e}`")
        else:
            await ctx.send(f"Load Success")

def run(bot):
    try:
        if settings.UseBetaBot:
            bot.run(settings.BetaToken, bot=True, reconnect=True)
        else:
            bot.run(settings.Token, bot=True, reconnect=True)
    except KeyboardInterrupt:
        bot.loop.run_until_complete(bot.logout())
    except:
        log.fatal(traceback.format_exc())