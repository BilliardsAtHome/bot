import discord
from discord.ext import tasks
from configparser import RawConfigParser
from break_info import BreakInfo
from database import Database
import time
from os import path

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

# Function
async def recordCheck(timestamp)-> BreakInfo | None:
    breaksDB = Database('breaks.db')
    oldBest = breaksDB.get_global_best_at_before(timestamp)
    newBest = breaksDB.get_new_global_best(timestamp)

    #TODO try except maybe not necessary? check BreakInfo vs None comparison and see if it catches
    try:
        if newBest > oldBest:
            return newBest
    except (TypeError) as e:
        print(e)
        return None


# bot stuff here
@client.event
async def on_ready():
    # Find channel through the client cache
    globals.server = client.get_guild(globals.serverID)
    globals.channel = client.get_channel(globals.channelID)
    assert globals.server is not None, "Can't find/access the discord server"
    assert globals.channel is not None, "Can't find/access the discord channel"
    task_watch_file.start()


# Periodically checks database for new top entry
#TODO change to a minute when done testing
@tasks.loop(seconds=5)
async def task_watch_file():
    if not path.exists('breaks.db'):
        return
    timestamp = globals.timestamp("config.ini")
    newBreak = await recordCheck(timestamp)
    if type(newBreak) != type(None):
        await globals.channel.send(f"User <@{newBreak.user}> got a {newBreak.sunk + newBreak.off} break with {newBreak.off} ball(s) off the table in {newBreak.frame / 60:.2f} seconds ({newBreak.frame} frames)!")


# TODO slash commands for show leaderboard, and show user (by ping)


# Start the bot
client.run(globals.token)