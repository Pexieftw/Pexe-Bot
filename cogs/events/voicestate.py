from discord.ext import commands
from pprint import pprint
import json
class VoiceState(commands.Cog):

    def __init__(self, bot):
        self.bot = bot    

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        voice_state = member.guild.voice_client
        if voice_state is None:
            return 
        if len(voice_state.channel.members) == 1:
            await voice_state.disconnect()   

async def setup(bot):
    await bot.add_cog(VoiceState(bot))