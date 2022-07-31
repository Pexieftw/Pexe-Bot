import discord
from discord.ext import commands
from configparser import ConfigParser
import datetime
class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='prefix', 
                    description='Shows the current prefix in this server',
                    aliases=['pre'])
    @commands.guild_only()
    async def prefix(self, ctx):
        settings = ConfigParser(interpolation=None)
        settings.read("settings.ini")
        try:
            prefix = settings['SERVER-PREFIXES'][str(ctx.guild.id)]
        except:
            prefix = settings['DEFAULT']['PREFIX']
            
        await ctx.send(f'Prefix used for this server is \'{prefix}\'')

    @commands.command(name='set_prefix', 
                    description='Sets the prefix used for your bot',
                    aliases=['setprefix', 'setp', 'set_p', 'sp'])
    @commands.guild_only()
    async def set_prefix(self, ctx, *, prefix):
        settings = ConfigParser(interpolation=None)
        settings.read("settings.ini")  
        if len(prefix) > 3:
            await ctx.send("Prefix needs to be 3 letters max")
        else:
            settings['SERVER-PREFIXES'][str(ctx.guild.id)] = prefix
            with open('settings.ini', 'w') as configfile:
                settings.write(configfile)
            await ctx.send(f'Prefix of this server successfully changed to \'{prefix}\'')

    @commands.command(name='set_language', 
                    description='Sets the language used in tts commands',
                    aliases=['setlanguage', 'setl', 'set_l', 'sl'])
    @commands.guild_only()
    async def set_language(self, ctx, *, lang):
        settings = ConfigParser(interpolation=None)
        settings.read("settings.ini")  
        if lang.lower() in settings['LANGUAGES'].keys():
            settings['SERVER-LANGUAGES'][str(ctx.guild.id)] = lang.lower()
            with open('settings.ini', 'w') as configfile:
                settings.write(configfile)
            await ctx.send(f"Server language successfully changed to \'{lang}\' - {settings['LANGUAGES'][lang]}")
        else:
            await ctx.send("That's an invalid language, Use `$llist` to see all the available languages")

    @commands.command(name='languages_list', 
                    description='Show a list of all the available languages for tts commands',
                    aliases=['llist', 'll'])
    @commands.guild_only()
    async def languages_list(self, ctx):
        settings = ConfigParser(interpolation=None)
        settings.read("settings.ini")
        embed=discord.Embed(title="Available TTS Languages", timestamp=datetime.datetime.utcnow())
        embed.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}")
        for language in settings['LANGUAGES'].items():
            embed.add_field(name=language[1], value="'"+language[0]+"'", inline=True)
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Settings(bot))