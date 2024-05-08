import discord
from discord import app_commands
from discord.ext import tasks
from configparser import RawConfigParser
from break_info import BreakInfo
import time
from os import path
from user_db import UserDB
from break_db import BreakDB


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
        self.checkTimer = int(parser.get("io", "check"))


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
async def recordCheck(timestamp)-> BreakInfo:
    breaksDB = BreakDB('allBreaks.db')
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

def hexN(value, bits):
    # mask to N bits
    bit_mask = (1 << bits) - 1
    value = value & bit_mask
    
    # remove 0x prefix
    s = hex(value)[2:]

    # leading zeroes
    num_nibbles = bits // 4
    num_zeroes = num_nibbles - len(s)
    return '0' * num_zeroes + s

# bot stuff here
@tree.command(
    name="ping",
    description="ping :3")
async def command_a(interaction: discord.Interaction):
    await interaction.response.send_message("h", ephemeral = True)
    print("Ping")

@tree.command(
    name="get-id",
    description="Get your unique ID to enter into the bruteforcer")
async def getID(interaction: discord.Interaction):
    uniqueUserDB = UserDB('users.db')
    uniqueID = uniqueUserDB.add_discord_id(str(interaction.user.id))
    idEmbed = discord.Embed(title=f"{interaction.user.name}'s Unique ID", color = discord.Colour.from_str(stringToColor(interaction.user.name)))
    idEmbed.add_field(name = "Unique ID", value = f"```{uniqueID}```")
    await interaction.response.send_message(embed = idEmbed, ephemeral = True)

@tree.command(name = "get-user", description = "Gets a user's high score")
@app_commands.describe(user = "What user?")
async def getUser(interaction: discord.Interaction, user: discord.User):
    usersDB = BreakDB('userBreaks.db')
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
    usersDB = BreakDB('userBreaks.db')
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
    breaksDB = BreakDB('allBreaks.db')
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
    breaksDB = BreakDB('allBreaks.db')
    break7 = breaksDB.count(f"(sunk+off) = 7 AND user = ?", (user.id,))
    break8 = breaksDB.count(f"(sunk+off) = 8 AND user = ?", (user.id,))
    break9 = breaksDB.count(f"(sunk+off) = 9 AND user = ?", (user.id,))
    outputString = f"```{"7:"} {break7:<4}\n{"8:"} {break8:<4}\n{"9:"} {break9:<4}```"

    statsEmbed = discord.Embed(title = f"{user.name}'s Break Stats", color =  globals.botColor)
    statsEmbed.add_field(name = "Breaks per Tier", value = outputString)
    await interaction.response.send_message(embed = statsEmbed, ephemeral = True)


@tree.command(name = "gecko", description = "Generate gecko code for a user's best break")
@app_commands.describe(user = "What user?")
async def getGecko(interaction: discord.Interaction, user: discord.User):
    usersDB = BreakDB('userBreaks.db')
    userBreak = usersDB.get_user_best(user.id)
    #TODO update with new gecko code when the time comes
    # {userBreak.seed:08X}
    response = f'''```
c22ba1ec 00000005
3fc0{hexN(userBreak.seed, 32)[:4]} 63de{hexN(userBreak.seed, 32)[4:]}
3fa08044 93ddc620
3d80802c 618c5d94
7d8903a6 4e800420
60000000 00000000
c20a6b3c 00000007
48000010 4e800021
{hexN(userBreak.posx, 32)} {hexN(userBreak.posy, 32)}
7c9f2378 3d80800c
618c9b14 7d8903a6
4e800421 4bffffe1
7fa802a6 e01d0000
f01f0020 00000000
c22beff8 00000004
4800000c 4e800021
{hexN(userBreak.power, 32)} 4bfffff9
7fe802a6 c03f0000
60000000 00000000
c22c5f38 00000003
3ba0{hexN(userBreak.getAimX(), 8)}{hexN(userBreak.up, 8)} 3fc08000
b3be2a00 4e800020
60000000 00000000
c22bfcb0 00000012
881f01fc 2c000000
40820080 3f408000
635a2a00 3f208044
633912b4 c0390000
8b1a0000 7f180775
41820030 4181000c
3b180001 4800000c
fc200850 3b18ffff
7fe3fb78 3d80802b
618cc238 7d8903a6
4e800421 9b1a0000
c0390004 fc200850
8b1a0001 2c180000
41820020 3b18ffff
7fe3fb78 3d80802b
618cc000 7d8903a6
4e800421 9b1a0001
806d91b0 00000000
c20f8350 00000002
38600000 4e800020
60000000 00000000
```'''
    geckoEmbed = discord.Embed(title = f"{user.name}'s Best Break", color = discord.Colour.from_str(stringToColor(user.name)))
    geckoEmbed.add_field(name = "Gecko Code:", value = response.upper())
    await interaction.response.send_message(embed = geckoEmbed, ephemeral = True)
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
@tasks.loop(seconds=globals.checkTimer)
async def task_watch_file():
    if not path.exists('allBreaks.db'):
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