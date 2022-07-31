import discord
from discord.ext import commands
from views import MovePage
import json


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.commands = json.load(open("Commands.json"))

    def _page_embed(self, num):
        num %= len(list(self.commands))
        pageTitle = list(self.commands)[num]
        embed = discord.Embed(color=0x0080ff, title=pageTitle)
        for key, val in self.commands[pageTitle].items():
            embed.add_field(
                name = key,
                value = val,
                inline = False
            )
            embed.set_footer(text=f"Page {num+1} of {len(list(self.commands))}")
        return embed

    @commands.command(name='help', 
                    description='Shows this message',
                    aliases=['h'])
    @commands.guild_only()
    async def help(self, ctx):
        view = MovePage()
        view.message = await ctx.send(embed=self._page_embed(0), view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))