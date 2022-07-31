import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
from configparser import ConfigParser
import youtube_dl
import random
from views import MoveQueue
from video import Video, VideoList
from utils import *

class GuildState:
    def __init__(self, vol):
        self.volume = vol
        self.playlist = []
        self.now_playing = None
        self.loop = False

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.states = {}

    def _skip(self, client, state):
        if client.is_playing():
            client.stop()
        if not len(state.playlist) > 0:
            state.now_playing = None

    def _play_song(self, client, state, song):
        if song is not None:
            state.now_playing = song
            source = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(
                    song.stream_url,
                    before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
                ), 
                volume=state.volume
            )
            def after_playing(err):
                if len(state.playlist) > 0:
                    next_song = state.now_playing if state.loop else state.playlist.pop(0)
                    self._play_song(client, state, next_song)
                else:
                    if state.loop:
                        self._play_song(client, state, state.now_playing)
                    else:
                        state.now_playing = None
        
            client.play(source, after=after_playing)

    def _get_queue_embed(self, state: GuildState, requester):
        embed = discord.Embed(
            color = 0xFFFFFF
        )
        embed.set_footer(
            text = f"Requested by {requester.name}",
            icon_url = requester.avatar.url
        )
        text = ""
        if len(state.playlist) == 0:
            text = "There's no songs in the queue" 
        elif len(state.playlist)>10:
            for index in range(0,10):
                text += f"**{index+1}** - `{convert(state.playlist[index].duration)}` - {state.playlist[index].title}\n"
        else:
            for index in range(0,len(state.playlist)):
                text += f"**{index+1}** - `{convert(state.playlist[index].duration)}` - {state.playlist[index].title}\n"      

        text += "\n**Loop State** = On\n" if state.loop else "\n**Loop State** = Off\n"

        embed.set_footer(text=f"Page 1 of {len(state.playlist)//10+1}")
        embed.add_field(
            name="**Current Queue:**",
            value=text,
            inline=False
        )
        return embed

    def _get_skip_embed(self, state: GuildState, requester):
        embed = discord.Embed(
            title = "**Song Skipped:**",
            description = state.now_playing.title,
            url = state.now_playing.video_url,
            color = 0xFFFFFF
        )
        embed.set_footer(
            text = f"Requested by {requester.name}",
            icon_url = requester.avatar.url
        )
        if state.now_playing.thumbnail:
            embed.set_thumbnail(url=state.now_playing.thumbnail)

        return embed

    def get_state(self, id):
        #gets the guild state if it exists otherwise it creates it
        if id in self.states:
            return self.states[id]
        else:
            settings = ConfigParser(interpolation=None)
            settings.read("settings.ini")
            try: #check if the server has any default volume 
                vol = settings['SERVER-VOLUMES'][str(id)]
            except: #else make it 0.5
                vol = settings['DEFAULT']['VOLUME']
            self.states[id] = GuildState(float(vol))
            return self.states[id]

    @commands.command(name='shuffle', 
                    description='Shuffles the current playlist',
                    aliases=['sh'])
    @commands.guild_only()
    async def shuffle(self, ctx):
        client = ctx.guild.voice_client
        state = self.get_state(ctx.guild.id)
        if state.loop:
            text = "Please turn off the loop first before using the shuffle command"
        else:
            if state.now_playing is not None and len(state.playlist) > 0:
                state.playlist.append(state.now_playing)
                random.shuffle(state.playlist)
                client.stop()

                text = "Playlist has been shuffeled"
            else:
                text = "You need at least 2 tracks in the playlist to use the shuffle command"
        
        embed = discord.Embed(
            description = text,
            color = 0xFFFFFF
        )

        await ctx.send(embed = embed)

    @commands.command(name='set_volume', 
                    description='Sets the volume of the music [between 0 and 1]',
                    aliases=['volume', 'vol', 'setv', 'sv'])
    @commands.guild_only()
    async def set_volume(self, ctx, *, volume):
        volume = float(volume)
        if volume >= 0 and volume <= 1:        
            state = self.get_state(ctx.guild.id)  
            settings = ConfigParser(interpolation=None)
            settings.read("settings.ini")  

            settings['SERVER-VOLUMES'][str(ctx.guild.id)] = str(volume)
            state.volume = volume

            with open('settings.ini', 'w') as configfile:
                settings.write(configfile)

            await ctx.send(f"Volume of the music was successfully changed to `{volume}`")
        else:
            await ctx.send("Volume needs to be between 0 and 1")

    @commands.command(name='leave', 
                    description='Leaves the voice channel',
                    aliases=['le'])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def leave(self, ctx):
        #leaves the voice channel if the user is already in one
        client = ctx.guild.voice_client
        state = self.get_state(ctx.guild.id)
        if client and client.channel:
            if ctx.author.voice.channel == client.channel:
                state.playlist = []
                state.now_playing = None
                await client.disconnect()
            else:
                await ctx.send("You need to be in the same channel as the bot to use the leave command")
        else:
            raise commands.CommandError("Not in a voice channel.")

    @commands.command(name='pause', 
                    description='Pauses or unpauses the current track',
                    aliases=['stop'])
    @commands.guild_only()
    async def pause(self, ctx):
        client = ctx.guild.voice_client
        if client and client.is_playing():
            client.pause()
        else:
            client.resume()

    @commands.command(name='skip', 
                    description='Skips into the next track',
                    aliases=['s', 'next', 'n'])
    @commands.guild_only()
    async def skip(self, ctx):
        state = self.get_state(ctx.guild.id)
        client = ctx.guild.voice_client
        if client and client.is_playing():
            embed = self._get_skip_embed(state, ctx.author)
            await ctx.send(embed = embed)
            self._skip(client,state)

    @commands.command(name='clear', 
                    description='Clears the current queue',
                    aliases=['clearqueue', 'cq'])
    @commands.guild_only()
    async def clear(self, ctx):
        state = self.get_state(ctx.guild.id)
        client = ctx.guild.voice_client
        if client and client.is_playing():
            client.stop()
            state.playlist = []

    @commands.command(name='loop', 
                    description='Loops the current track',
                    aliases=['l'])
    @commands.guild_only()
    async def loop(self, ctx):
        state = self.get_state(ctx.guild.id)
        if state.loop:
            state.loop = False
            await ctx.send("Loop deactivated")
        else:
            state.loop = True
            await ctx.send("Loop activated")

    @commands.command(name='queue', 
                    description='Shows the current playlist',
                    aliases=['q', 'playlist', 'pl'])
    @commands.guild_only()
    async def queue(self, ctx):
        state = self.get_state(ctx.guild.id)
        client = ctx.guild.voice_client
        if client is None:
            state.playlist = []
            state.now_playing = None

        new_state = GuildState(0.5)
        new_state.loop = state.loop
        new_state.now_playing = state.now_playing
        new_state.playlist = state.playlist.copy()
        new_state.playlist.insert(0,new_state.now_playing)

        is_onepage = True if len(new_state.playlist)<=10 else False 
        view = MoveQueue(new_state, is_onepage)

        view.message = await ctx.send(embed=self._get_queue_embed(new_state, ctx.author), view=view)

    @commands.command(name='play', 
                    description='Plays a video from youtube',
                    aliases=['song', 'p'])
    @commands.guild_only()
    async def play(self, ctx, *, url):
        client = ctx.guild.voice_client
        state = self.get_state(ctx.guild.id)  # get the guild's state
        if ctx.author.voice != None:
            if ctx.voice_client == None:
                client = await ctx.author.voice.channel.connect()
                #empty the playlist
                if len(state.playlist) > 0:
                    state.now_playing = None
                    state.playlist = []
            else:
                JoinChannel = True
                for voice_client in self.bot.voice_clients:
                    if voice_client.channel == ctx.author.voice.channel:
                        JoinChannel = False
                        break
                if JoinChannel:
                    await ctx.voice_client.disconnect()
                    client = await ctx.author.voice.channel.connect()
                    #empty the playlist
                    if len(state.playlist) > 0:
                        state.now_playing = None
                        state.playlist = []
            try:
                videolist = VideoList(url, ctx.author)
            except youtube_dl.DownloadError as e:
                await ctx.send("There was an error downloading your video, Sorry.")
                return
            if len(state.playlist) == 0 and not client.is_playing(): 
                #if there's no track playing, then start playing this current track
                to_play = videolist.videos.pop(0)
                self._play_song(client, state, to_play)
                #if there's more than 1 track, add the rest to the queue
                for video in videolist.videos:
                    state.playlist.append(video)
            else:
                #otherwise add all to the queue
                for video in videolist.videos:
                    state.playlist.append(video)

                to_play = videolist.videos[0]
            if videolist.is_playlist:
                await ctx.send(embed=videolist.get_embed())
            else:
                await ctx.send(f"Added to the queue (#{len(state.playlist)+1})", embed=to_play.get_embed())
        else:
            await ctx.send("You need to connect to a channel first")

async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))