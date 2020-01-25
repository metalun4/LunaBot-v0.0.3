import discord
import asyncio
from random import randint
from discord.ext import commands


class Pug(commands.Cog):
    """PUG commands for bot"""

    def __init__(self, bot):
        self.bot = bot

        self.pugs = dict()

    def restart_pug(self, channel):
        # Reset everything
        for player in self.pugs[channel]["players"]:
            self.pugs[channel]["players"].remove(player)
        if self.pugs[channel]["state"] is "add":
            del self.pugs[channel]

    def pick_captains(self, guild, channel):
        # Pick random two captains from list
        self.pugs[channel]["captain1"] = self.pugs[channel]["signed_up"][
            randint(0, len(self.pugs[channel]["signed_up"]) - 1)]
        self.pugs[channel]["signed_up"].remove(self.pugs[channel]["captain1"])
        self.pugs[channel]["team_one"].append(guild.get_member(self.pugs[channel]["captain1"]))

        self.pugs[channel]["captain2"] = self.pugs[channel]["signed_up"][
            randint(0, len(self.pugs[channel]["signed_up"]) - 1)]
        self.pugs[channel]["signed_up"].remove(self.pugs[channel]["captain2"])
        self.pugs[channel]["team_two"].append(guild.get_member(self.pugs[channel]["captain2"]))

    def format_embed(self, picking, guild, channel):
        # Embed formatting
        if picking is True:
            e = discord.Embed(title="PUG Teams | Captains are picking", color=0xFFFF00)
        else:
            e = discord.Embed(title="PUG Teams | Teams are ready", color=0x008000)

        e.add_field(name="Team 1", value="\n".join([str(p) for p in self.pugs[channel]["team_one"]]))
        e.add_field(name="Team 2", value="\n".join([str(p) for p in self.pugs[channel]["team_two"]]))

        if len(self.pugs[channel]["signed_up"]) > 0:
            e.add_field(name="Available Players",
                        value="\n".join([str(guild.get_member(p)) for p in self.pugs[channel]["signed_up"]]))
            return e
        else:
            return e

    @commands.command(pass_context=True, aliases=["a"], no_pm=True)
    async def add(self, ctx):
        """ ---Adds the player in pug"""
        msg = ctx.message
        user = msg.author.id
        channel = msg.channel.id

        if channel not in self.pugs:
            self.pugs[channel] = {"players": [], "signed_up": [], "size": None, "state": "add", "picks_remain": 1,
                                  "team_one": [], "team_two": [], "captain1": None, "captain2": None,
                                  "one_picking": False, "two_picking": False}

        if self.pugs[channel]["size"] is None:
            await ctx.send(f"Set team size first")
            return

        if self.pugs[channel]["state"] is not "add":
            await ctx.send(f"<@{user}>, PUG is currently running please wait")
            return

        if user in self.pugs[channel]["players"]:
            await ctx.send(f"<@{user}>, you are already in")
            return

        self.pugs[channel]["players"].append(user)

        await ctx.send(f"<@{user}>, added to PUG!")

        if len(self.pugs[channel]["players"]) >= self.pugs[channel]["size"] * 2:
            self.pugs[channel]["state"] = "ready"
            await ctx.send("PUG is ready, type .ready or .r")
            await asyncio.sleep(60)
            if self.pugs[channel]["state"] is "ready":
                await ctx.send("Timeout these players are not ready: {}".format(
                    "".join([str("<@" + p + "> ") for p in self.pugs[channel]["players"]])))
                self.restart_pug(channel)
                self.pugs[channel]["state"] = "add"

    @commands.command(pass_context=True, aliases=["l"], no_pm=True)
    async def leave(self, ctx):
        """ ---Removes the player"""
        msg = ctx.message
        user = msg.author.id
        channel = msg.channel.id

        if self.pugs[channel]["state"] != "add":
            await ctx.send(f"<@{user}>, can\"t do that right now!")
            return
        if user in self.pugs[channel]["players"]:
            self.pugs[channel]["players"].remove(user)
            await ctx.send(f"<@{user}>, removed")
        else:
            await ctx.send(f"<@{user}>, you are not in")

    @commands.command(pass_context=True, aliases=["r"], no_pm=True)
    async def ready(self, ctx):
        """ ---Readies the player"""
        msg = ctx.message
        user = msg.author.id
        channel = msg.channel.id
        guild = msg.guild

        if self.pugs[channel]["state"] is not "ready":
            await ctx.send(f"<@{user}>, you cannot ready up right now")
            return

        if user in self.pugs[channel]["players"]:
            self.pugs[channel]["players"].remove(user)
            self.pugs[channel]["signed_up"].append(user)
            await ctx.send("READY!")
        elif user in self.pugs[channel]["signed_up"]:
            await ctx.send(f"<@{user}>, you are already readied")
        else:
            await ctx.send(f"<@{user}>, another PUG is in progress wait for other one!")

        if len(self.pugs[channel]["signed_up"]) >= self.pugs[channel]["size"] * 2:
            await ctx.trigger_typing()
            self.pick_captains(guild, channel)
            if self.pugs[channel]["captain1"] is not None and self.pugs[channel]["captain2"] is not None:
                self.pugs[channel]["state"] = "pick"
                await ctx.send(embed=self.format_embed(picking=True, guild=guild, channel=channel),
                               content="PUG is starting, captains are: <@{}>, <@{}>".format(
                                   self.pugs[channel]["captain1"], self.pugs[channel]["captain2"]))
                self.pugs[channel]["one_picking"] = True
                await ctx.send("<@{}> is picking. Can pick {} player".format(self.pugs[channel]["captain1"],
                                                                             self.pugs[channel]["picks_remain"]))

    @commands.command(pass_context=True, aliases=["p"], no_pm=True)
    async def pick(self, ctx, member: discord.Member):
        """ ---Picks player for the team, only captains can use"""
        msg = ctx.message
        user = msg.author.id
        channel = msg.channel.id
        guild = msg.guild

        if self.pugs[channel]["state"] is not "pick":
            await ctx.send(f"<@{user}>, start a pug first")
            return

        if member.id not in self.pugs[channel]["signed_up"]:
            await ctx.send(f"<@{user}>, this player is not available try different one")
            return

        if user is self.pugs[channel]["captain1"] and self.pugs[channel]["one_picking"] is True:
            self.pugs[channel]["team_one"].append(member)
            self.pugs[channel]["signed_up"].remove(member.id)
            self.pugs[channel]["picks_remain"] = self.pugs[channel]["picks_remain"] - 1
            if len(self.pugs[channel]["team_one"]) + len(self.pugs[channel]["team_two"]) == self.pugs[channel][
                "size"] * 2:
                await ctx.send(embed=self.format_embed(picking=False, guild=guild, channel=channel),
                               content="LET\"S GOOOOOOOO!")
                self.pugs[channel]["state"] = "add"
                return
            if self.pugs[channel]["picks_remain"] == 0:
                self.pugs[channel]["one_picking"] = False
                self.pugs[channel]["two_picking"] = True
                if len(self.pugs[channel]["signed_up"]) == 1:
                    self.pugs[channel]["picks_remain"] = 1
                else:
                    self.pugs[channel]["picks_remain"] = 2
                await ctx.send(embed=self.format_embed(picking=True, guild=guild, channel=channel),
                               content=f"<@{self.pugs[channel]['captain1']}> is picking. Can pick {self.pugs[channel]['picks_remain']} players")
                return
            await ctx.send(embed=self.format_embed(picking=True, guild=guild, channel=channel))
            return

        if user is self.pugs[channel]["captain2"] and self.pugs[channel]["two_picking"] is True:
            self.pugs[channel]["team_two"].append(member)
            self.pugs[channel]["signed_up"].remove(member.id)
            self.pugs[channel]["picks_remain"] = self.pugs[channel]["picks_remain"] - 1
            if len(self.pugs[channel]["team_one"]) + len(self.pugs[channel]["team_two"]) == self.pugs[channel][
                "size"] * 2:
                await ctx.send(embed=self.format_embed(picking=False, guild=guild, channel=channel),
                               content="LET\"S GOOOOOOOO!")
                self.pugs[channel]["state"] = "add"
                return
            if self.pugs[channel]["picks_remain"] == 0:
                self.pugs[channel]["two_picking"] = False
                self.pugs[channel]["one_picking"] = True
                if len(self.pugs[channel]["signed_up"]) == 1:
                    self.pugs[channel]["picks_remain"] = 1
                else:
                    self.pugs[channel]["picks_remain"] = 2
                await ctx.send(embed=self.format_embed(picking=True, guild=guild, channel=channel),
                               content=f"<@{self.pugs[channel]['captain2']}> is picking. Can pick {self.pugs[channel]['picks_remain']} players")
                return
            await ctx.send(embed=self.format_embed(picking=True, guild=guild, channel=channel))
            return

    @commands.command(pass_context=True, aliases=["ss"], no_pm=True)
    async def setsize(self, ctx, size):
        """ ---Sets team size for the PUG"""
        msg = ctx.message
        user = msg.author.id
        channel = msg.channel.id

        if channel not in self.pugs:
            self.pugs[channel] = {"players": [], "signed_up": [], "size": None, "state": "add", "picks_remain": 1,
                                  "team_one": [], "team_two": [], "captain1": None, "captain2": None,
                                  "one_picking": False, "two_picking": False}

        if len(self.pugs[channel]["players"]) > 0 or self.pugs[channel]["state"] is not "add":
            await ctx.send("Can\"t change team size right now")
            return

        try:
            self.pugs[channel]["size"] = int(size)
        except KeyError:
            await ctx.send("Team size has to be a number")
            return
        await ctx.send(f"Team size set to {self.pugs[channel]['size']} by <@{user}>")

    @commands.command(pass_context=True, no_pm=True)
    async def reset(self, ctx):
        """ ---Resets the PUG"""
        msg = ctx.message
        channel = msg.channel.id

        try:
            self.pugs[channel]["state"] = "add"
            self.restart_pug(channel)
            await ctx.send("Restarted the PUG")
        except KeyError:
            await ctx.send("Start a PUG first")

    @commands.command(pass_context=True, no_pm=True)
    async def status(self, ctx):
        """ ---Shows the status of PUG"""
        msg = ctx.message
        channel = msg.channel.id
        guild = msg.guild

        if channel not in self.pugs:
            await ctx.send("Start a PUG first")
            return

        if self.pugs[channel]["state"] == "add" and len(self.pugs[channel]["players"]) > 0:
            await ctx.send(f"Not enough players for PUG {len(self.pugs[channel]['players'])}/{self.pugs[channel]['size']*2}")
            await ctx.send("\n".join([str(guild.get_member(p)) for p in self.pugs[channel]["players"]]))
        elif self.pugs[channel]["state"] == "ready":
            await ctx.send(f"{len(self.pugs[channel['players']])} player is ready. Non ready players:")
            await ctx.send("\n".join([str(guild.get_member(p)) for p in self.pugs[channel]["players"]]))
        elif self.pugs[channel]["state"] == "pick":
            await ctx.send("Shhhh! Captains are picking.")
        elif self.pugs[channel]["state"] == "add" and len(self.pugs[channel]["players"]) == 0:
            await ctx.send("No one wants to play PUG <:monkaS:587398512854040576>")
        else:
            await ctx.send("Start a PUG first")


def setup(bot):
    bot.add_cog(Pug(bot))
