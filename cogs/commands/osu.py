from variables import *
import discord
from discord.ext import commands
import datetime
from datetime import datetime
from utils import *

class Profile():
    def __init__(self, profile):
        self.name = profile['username']
        self.id = profile['id']
        self.cc = profile['country_code']
        self.avatar_url = profile['avatar_url']
        self.cover_url = profile['cover_url']
        self.last_visit = profile['last_visit']
        self.join_date = datetime.fromisoformat(profile['join_date']).replace(tzinfo=None)
        self.pp = "{:,}".format(profile['statistics']['pp'])
        self.level = profile['statistics']['level']['current']
        self.progress = profile['statistics']['level']['progress']
        self.global_rank = profile['statistics']['global_rank']
        self.country_rank = profile['statistics']['country_rank']
        self.accuracy = "{:.2f}".format(profile['statistics']['hit_accuracy'])
        self.play_time = profile['statistics']['play_time']
        self.play_count = "{:,}".format(profile['statistics']['play_count'])
        self.x = profile['statistics']['grade_counts']['ss']
        self.xh = profile['statistics']['grade_counts']['ssh']
        self.s = profile['statistics']['grade_counts']['s']
        self.sh = profile['statistics']['grade_counts']['sh']
        self.a = profile['statistics']['grade_counts']['a']

class Osu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='osu', 
                    description='Shows your osu! profile',
                    aliases=['op', 'profile'])
    @commands.guild_only()
    async def osu(self, ctx, *, name):
        # Get User Data
        User = Profile(get_profile(name))
        # Get Embed Text
        if User.global_rank and User.country_rank:
            User.global_rank = "{:,}".format(User.global_rank)
            User.country_rank = "{:,}".format(User.country_rank)
            text = f'**Rank:** :earth_africa: #{User.global_rank} - :flag_{User.cc.lower()}: #{User.country_rank}\n' 
        else:
            text = '**Rank:** Unranked\n'
        text += f'**PP:** {User.pp} - **Accuracy:** {User.accuracy}%\n'
        text += f'**Level:** {User.level} {progress_bar(User.progress)} {User.level+1} `{User.progress}%`\n'
        text += f'**Grades:** {Rank_XH}`{User.xh}` {Rank_X}`{User.x}` {Rank_SH}`{User.sh}` {Rank_S}`{User.s}` {Rank_A}`{User.a}`\n'
        text += f'**Playcount:** {User.play_count} - **Playtime:** {User.play_time//3600} hours\n'
        if User.last_visit: 
            text += f'**Last Visit:** `{datetime.fromisoformat(User.last_visit).replace(tzinfo=None)}`\n'
        date = datetime.utcnow() - User.join_date
        text += f'**Join Date:** `{User.join_date}` ({date.days} days ago)\n'
        # Embed
        embed = discord.Embed(
            title=f"osu profile of **{User.name}**",
            description=text,
            url="https://osu.ppy.sh/users/{User.id}"
        )
        embed.set_footer(
            text=f"Requested by {ctx.author.name}",
            icon_url=ctx.author.avatar.url
        )
        embed.set_thumbnail(url=User.avatar_url)
        if User.cover_url != 'https://osu.ppy.sh/images/headers/profile-covers/c6.jpg':
            embed.set_image(url=User.cover_url)
        await ctx.reply(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Osu(bot))