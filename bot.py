import discord
from configparser import RawConfigParser


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

# Globals
globals = Globals("config.ini")
client = discord.Client(intents=discord.Intents.default())


# bot stuff here
@client.event
async def on_ready():
    # Called once when the bot establishes a connection with the Discord API.

    # Find channel through the API
    globals.server = await client.get_guild(globals.serverID)
    globals.channel = await client.get_channel(globals.channelID)

    assert globals.server is not None, "Can't find/access the discord server"
    assert globals.channel is not None, "Can't find/access the discord channel"


# TODO task to check database for new top entry


# TODO slash commands for show leaderboard, and for claim client ID?


# Start the bot
client.run(globals.token)