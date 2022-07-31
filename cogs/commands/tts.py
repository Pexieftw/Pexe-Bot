import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import gtts
import os
from gtts import gTTS
from configparser import ConfigParser



class Tts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='voice', 
                    description='Plays the text you typed if you\'re currently in a voice channel',
                    aliases=['v'])
    @commands.guild_only()
    async def voice(self, ctx, *, arg=""):
        if len(arg)>0 and len(arg)<1000:
            if ctx.author.voice != None:
                if ctx.voice_client == None:
                    VoiceClient = await ctx.author.voice.channel.connect()
                else:
                    JoinChannel = True
                    for voice_client in self.bot.voice_clients:
                        if voice_client.channel == ctx.author.voice.channel:
                            VoiceClient = voice_client
                            JoinChannel = False
                            break
                    if JoinChannel:
                        await ctx.voice_client.disconnect()
                        VoiceClient = await ctx.author.voice.channel.connect()
                settings = ConfigParser(interpolation=None)
                settings.read("settings.ini")
                try:
                    lang = settings['SERVER-LANGUAGES'][str(ctx.guild.id)]
                except:
                    lang = settings['DEFAULT']['LANGUAGE']
                output = gTTS(text=arg, lang=lang, slow=False)
                if not os.path.exists('tts'):
                    os.makedirs('tts')
                output.save(f"tts//{ctx.guild.id}.mp3")
                voice = FFmpegPCMAudio(f"tts//{ctx.guild.id}.mp3")
                VoiceClient.play(voice)
            else:
                await ctx.send("You need to connect to a channel first")
        else:
            await ctx.send("Message need to contain between 0 and 1000 letters")


async def setup(bot: commands.Bot):
    await bot.add_cog(Tts(bot))