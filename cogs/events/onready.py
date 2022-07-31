from discord.ext import commands
from datetime import datetime
class OnReady(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Bot connected as: {self.bot.user.name}\n-------------------------")

async def setup(bot):
    await bot.add_cog(OnReady(bot))
