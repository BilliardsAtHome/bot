import discord
from discord import app_commands
from discord.ext import tasks
from configparser import RawConfigParser
from break_info import BreakInfo
from database import Database
import time
from os import path
from hashlib import md5


# Classes
class Globals:
    def __init__(self, path: str):
        parser = RawConfigParser()
        parser.read(path, encoding="utf-8")

        self.serverID = int(parser.get("discord", "server"))
        self.channelID = int(parser.get("discord", "channel"))
        self.role = int(parser.get("discord", "role"))
        self.botColor = discord.Colour.from_str("#" + str(parser.get("discord", "color")))
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
        return oldTimestamp

# Globals
globals = Globals("config.ini")
client = discord.Client(intents=discord.Intents.default())
tree = app_commands.CommandTree(client)


# Function
async def recordCheck(timestamp)-> BreakInfo | None:
    breaksDB = Database('breaks.db')
    oldBest = breaksDB.get_global_best_at_before(timestamp)
    newBest = breaksDB.get_new_global_best(timestamp)

    try:
        if newBest > oldBest:
            return newBest
    except (TypeError) as e:
        print(e)
        return None


def stringToColor(string: str):
    val1 = format(goodHash(string) % 255, '02x')
    val2 = format(goodHash(string[1:] + string[:1]) % 255, '02x')
    val3 = format(goodHash(string[2:] + string[:2]) % 255, '02x')
    return "#" + val1 + val2 + val3


def goodHash(string):
    x = 11012001182514 
    for c in string:
        x = ((x << 5) + x) + ord(c)
    return x ^ len(string)


# bot stuff here
@tree.command(
    name="ping",
    description="ping :3")
async def command_a(interaction: discord.Interaction):
    await interaction.response.send_message("h", ephemeral = True)


@tree.command(name = "get-user", description = "Gets a user's high score")
@app_commands.describe(user = "What user?")
async def getUser(interaction: discord.Interaction, user: discord.User):
    usersDB = Database('users.db')
    if usersDB.contains_user(user.id):
        bestBreak: BreakInfo = usersDB.get_user_best(user.id)
        userEmbed = discord.Embed(title = f"{user.name} High Score", color = discord.Colour.from_str(stringToColor(user.name)))
        userEmbed.add_field(name = "Out of Play", value = bestBreak.sunk + bestBreak.off, inline = True)
        userEmbed.add_field(name = "Off table", value = bestBreak.off, inline = True)
        userEmbed.add_field(name = "Foul", value = bestBreak.foul, inline = True)
        userEmbed.add_field(name = "Time", value = f"{bestBreak.frame/60:.2f}", inline = True)
        userEmbed.add_field(name = "Frames", value = f"{bestBreak.frame}", inline = True)

        await interaction.response.send_message(embed = userEmbed, ephemeral = True)
    else:
        await interaction.response.send_message(f"<@{user.id}> does not have a high score.", ephemeral = True)


@tree.command(name = "get-leaderboard", description = "Gets the high scores leaderboard")
async def getLeaderboard(interaction: discord.Interaction):
    usersDB = Database('users.db')
    usersList: list = usersDB.get_top_10()
    longestName = 0
    usernamesList = []
    for user in usersList:
        userObject = await client.fetch_user(user.user)
        userName = str(userObject.name)
        if len(userName) > longestName:
            longestName = len(userName)

    outputString = f"```{'name':<{longestName + 2}} {'balls':<6} {'off':<4} {'foul':<6} {'frame':<6}\n"
    for breakObject in usersList:
        userObject = await client.fetch_user(breakObject.user)
        userName = str(userObject.name)
        outputString += f"{userName:<{longestName + 2}} {breakObject.sunk + breakObject.off:<6} {breakObject.off:<4} {breakObject.foul!s:<6} {breakObject.frame:<6}\n"
    outputString += "```"

    leaderboardEmbed = discord.Embed(title = "Global Leaderboard", color = globals.botColor)
    leaderboardEmbed.add_field(name = "Top 10 users", value = outputString)
    await interaction.response.send_message(embed = leaderboardEmbed, ephemeral = True)


@tree.command(name = "stats", description = "Break statistics")
async def globalStats(interaction: discord.Interaction):
    breaksDB = Database('breaks.db')
    break7 = breaksDB.count("(sunk+off) = 7")
    break8 = breaksDB.count("(sunk+off) = 8")
    break9 = breaksDB.count("(sunk+off) = 9")
    outputString = f"```{"7:"} {break7:<4}\n{"8:"} {break8:<4}\n{"9:"} {break9:<4}```"

    statsEmbed = discord.Embed(title = "Global Break Stats", color =  globals.botColor)
    statsEmbed.add_field(name = "Breaks per Tier", value = outputString)
    await interaction.response.send_message(embed = statsEmbed, ephemeral = True)


@tree.command(name = "user-stats", description = "Break statistics for a specific user")
@app_commands.describe(user = "What user?")
async def userStats(interaction: discord.Interaction, user: discord.User):
    breaksDB = Database('breaks.db')
    break7 = breaksDB.count(f"(sunk+off) = 7 AND user = {user.id}")
    break8 = breaksDB.count(f"(sunk+off) = 8 AND user = {user.id}")
    break9 = breaksDB.count(f"(sunk+off) = 9 AND user = {user.id}")
    outputString = f"```{"7:"} {break7:<4}\n{"8:"} {break8:<4}\n{"9:"} {break9:<4}```"

    statsEmbed = discord.Embed(title = f"{user.name}'s Break Stats", color =  globals.botColor)
    statsEmbed.add_field(name = "Breaks per Tier", value = outputString)
    await interaction.response.send_message(embed = statsEmbed, ephemeral = True)


@tree.command(name = "gecko", description = "Generate gecko code for a user's best break")
@app_commands.describe(user = "What user?")
async def getGecko(interaction: discord.Interaction, user: discord.User):
    #TODO make gecko code for a user's best break
    pass


@tree.command(name='sync', description='Owner only')
async def sync(interaction: discord.Interaction):
    if interaction.user.id == 439441145466978305:
        sync = await tree.sync()
        await interaction.response.send_message(f"Synced {len(sync)} commands", ephemeral = True)
    else:
        await interaction.response.send_message('You must be the owner to use this command!', ephemeral = True)


@client.event
async def on_ready():
    # Find channel through the client cache
    globals.server = client.get_guild(globals.serverID)
    globals.channel = client.get_channel(globals.channelID)
    assert globals.server is not None, "Can't find/access the discord server"
    assert globals.channel is not None, "Can't find/access the discord channel"
    task_watch_file.start()


# Periodically checks database for new top entry
@tasks.loop(seconds=60)
async def task_watch_file():
    if not path.exists('breaks.db'):
        return
    timestamp = globals.timestamp("config.ini")
    
    if newBreak := await recordCheck(timestamp):
        user = await client.fetch_user(newBreak.user)
        recordEmbed = discord.Embed(title = f"New Break Record by {user.name}", color = discord.Colour.from_str(stringToColor(user.name)))
        recordEmbed.add_field(name = "Out of Play", value = newBreak.sunk + newBreak.off, inline = True)
        recordEmbed.add_field(name = "Off table", value = newBreak.off, inline = True)
        recordEmbed.add_field(name = "Foul", value = newBreak.foul, inline = True)
        recordEmbed.add_field(name = "Time", value = f"{newBreak.frame/60:.2f}", inline = True)
        recordEmbed.add_field(name = "Frames", value = f"{newBreak.frame}", inline = True)
        recordEmbed.set_footer(text = user.id)
        await globals.channel.send(f"<@&{globals.role}>",embed = recordEmbed)


# Start the bot
client.run(globals.token)