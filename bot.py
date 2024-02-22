import discord
from discord.ext import tasks
from configparser import RawConfigParser
from break_info import BreakInfo
from database import Database
import time

#TODO figure out embed builder for leaderboard (buttons to nav pages)
#TODO slash commands
    # leaderboard
    # user (basically leaderboard but for one person)
#! figure out server stuff, nginx/gunicorn

# Classes
class Globals:
    def __init__(self, path: str):
        parser = RawConfigParser()
        parser.read(path, encoding="utf-8")

        self.serverID = int(parser.get("discord", "server"))
        self.channelID = int(parser.get("discord", "channel"))
        self.token = str(parser.get("secrets", "token"))
        self.appID = int(parser.get("secrets", "appID"))

        self.server = None
        self.channel = None

    def timestamp(self, path):
        parser = RawConfigParser()
        parser.read(path, encoding="utf-8")
        
        oldTimestamp = int(parser.get("io", "timestamp"))
        newTimestamp = round(time.time())
        parser['io']['timestamp'] = str(newTimestamp)
        with open(path, 'w') as configfile:
            parser.write(configfile)
        print(f"wrote {newTimestamp}")

        return oldTimestamp

# Globals
globals = Globals("config.ini")
client = discord.Client(intents=discord.Intents.default())


# bot stuff here
@client.event
async def on_ready():
    # Find channel through the API
    globals.server = client.get_guild(globals.serverID)
    globals.channel = client.get_channel(globals.channelID)
    assert globals.server is not None, "Can't find/access the discord server"
    assert globals.channel is not None, "Can't find/access the discord channel"
    task_watch_file.start()


# TODO task to check database for new top entry
@tasks.loop(seconds=5)
async def task_watch_file():
    print("a")
    print(globals.timestamp("config.ini"))


# TODO slash commands for show leaderboard, and show user (by ping)


# Start the bot
client.run(globals.token)