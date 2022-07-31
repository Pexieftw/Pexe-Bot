import asyncio
import discord
from discord.ext import commands
from configparser import ConfigParser
import os

def get_prefix(bot, msg):
    settings = ConfigParser(interpolation=None)
    settings.read("settings.ini")
    prefix = settings['DEFAULT']['PREFIX']
    if str(msg.guild.id) in settings['SERVER-PREFIXES']:
        prefix = settings['SERVER-PREFIXES'][str(msg.guild.id)]
    return commands.when_mentioned_or(prefix)(bot, msg)

activity = discord.Activity(type=discord.ActivityType.listening, name="$help")
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=get_prefix, description="TTS Bot", help_command=None,
                    case_insensitive=True, intents=intents, activity=activity)

async def load_extensions():
    for file in os.listdir("./cogs/events"):
        if file.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.events.{file[:-3]}")
            except Exception as Error:
                print(f"Couldn't load event {file[:-3]} due to {Error}")
    for file in os.listdir("./cogs/commands"):
        if file.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.commands.{file[:-3]}")
            except Exception as Error:
                print(f"Couldn't load command {file[:-3]} due to {Error}")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(os.environ.get('TOKEN'))

asyncio.run(main())